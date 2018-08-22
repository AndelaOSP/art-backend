# -*- coding: UTF-8 -*-
import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q

from tableschema import Table, validate, exceptions
from tqdm import tqdm

from core.models.asset import (
    Asset,
    AssetCategory,
    AssetSubCategory,
    AssetType,
    AssetMake,
    AssetModelNumber,
    AssetStatus,
    AssetSpecs,
    AssetCondition
)

User = get_user_model()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_PATH,
    'assets.csv'
)

SCHEMA_PATH = os.path.join(
    BASE_PATH,
    'schema.json'
)

SKIPPED_ASSETS_FILE = os.path.join(
    BASE_PATH,
    'skipped.csv'
)


def write_exception_to_console(error_message):
    print(error_message)


def write_exception_to_file(error_message, row_data):
    with open(SKIPPED_ASSETS_FILE, 'w') as out_file:
        out_file.write(f"{error_message} {row_data}")


def load_data_from_local_csv(csv_file=DATA_FILE):
    table = Table(csv_file, schema=SCHEMA_PATH)

    try:
        valid = validate(table.schema.descriptor)
        if valid:
            for keyed_row in table.iter(keyed=True):
                yield keyed_row
    except exceptions.ValidationError as exception:
        # for error in exception.errors:
        #     print(error)
        pass
    except exceptions.CastError as cast_exception:
                    if cast_exception.errors:
                        write_exception_to_console(cast_exception)


def save_to_models(validated_data):
    asset_category, _ = AssetCategory.objects.get_or_create(
        category_name=validated_data.get('category_name')
    )
    asset_sub_category, _ = AssetSubCategory.objects.get_or_create(
        sub_category_name=validated_data.get('sub_category_name'),
        asset_category=asset_category
    )
    asset_type, _ = AssetType.objects.get_or_create(
        asset_type=validated_data.get('asset_type'),
        asset_sub_category=asset_sub_category
    )
    asset_make, _ = AssetMake.objects.get_or_create(
        make_label=validated_data.get('make_label'),
        asset_type=asset_type
    )
    asset_model_number, _ = AssetModelNumber.objects.get_or_create(
        model_number=validated_data.get('model_number'),
        make_label=asset_make
    )
    asset_spec, _ = AssetSpecs.objects.get_or_create(
        memory=validated_data.get('memory'),
        storage=validated_data.get('storage'),
        processor_type=validated_data.get('processor_type'),
        year_of_manufacture=validated_data.get('year_of_manufacture')
    )

    try:
        # import ipdb; ipdb.set_trace()
        asset = Asset.objects.get(
            Q(asset_code=validated_data.get('asset_code')), Q(serial_number=validated_data.get('serial_number'))
        )
        asset.model_number = asset_model_number
    except ObjectDoesNotExist:
        try:
            asset = Asset.objects.get(
                Q(asset_code=validated_data.get('asset_code')) | Q(serial_number=validated_data.get('serial_number'))
            )
            asset.asset_code = validated_data.get('asset_code')
            asset.serial_number = validated_data.get('serial_number')
            asset.model_number = asset_model_number
            asset.verified = validated_data.get('verified') or True
        except MultipleObjectsReturned:
            return
        except ObjectDoesNotExist:
            asset = Asset(
                asset_code=validated_data.get('asset_code'),
                serial_number=validated_data.get('serial_number'),
                model_number=asset_model_number
            )
    # asset.verified = validated_data.get('verified') or True

    try:
        user_email = email = validated_data.get('assigned_to')
        if user_email:
            User.objects.create(email=user_email)
    except IntegrityError:
        assigned_to = User.objects.get(
            email=user_email
        )
        asset.assigned_to = assigned_to.assetassignee

    asset.save()

    asset_notes = validated_data.get('notes')
    if asset_notes:
        AssetCondition.objects.create(
            asset=asset,
            notes=asset_notes
        )
    specified_status = validated_data.get('current_status')
    if specified_status:
        AssetStatus.objects.create(
            asset=asset,
            current_status=specified_status
        )


class Command(BaseCommand):
    help = 'Bulk create Assets from local or remote csv file'

    # def add_arguments(self, parser):
    #     parser.add_argument('csv_file')

    def handle(self, *args, **options):
        # filepath = options['csv_file']
        validated_data_generator = load_data_from_local_csv()

        with tqdm(iterable=validated_data_generator) as progress:
            for row_id, row_data in enumerate(validated_data_generator):
                try:
                    progress.write(f'processing row number {row_id}')
                    # import ipdb; ipdb.set_trace()
                    save_to_models(row_data)
                    progress.update()
                except exceptions.CastError as cast_exception:
                    if cast_exception.errors:
                        for error in cast_exception.errors:
                            # import ipdb; ipdb.set_trace()
                            write_exception_to_file(error, row_data)
