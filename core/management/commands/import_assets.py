# -*- coding: UTF-8 -*-
import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from tableschema import Table, validate, exceptions

from core.models.asset import (
    Asset,
    AssetCategory,
    AssetSubCategory,
    AssetType,
    AssetMake,
    AssetModelNumber,
    AssetSpecs,
    AssetCondition
)
from core.managers import CaseInsensitiveQuerySet

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


def save_to_models(validated_data):
    asset = None
    user_email = None

    category_name = validated_data.get('category_name')
    if category_name:
        asset_category, _ = AssetCategory.objects.get_or_create(
            category_name=category_name
        )
    else:
        return
    asset_sub_category, _ = AssetSubCategory.objects.get_or_create(
        sub_category_name=validated_data.get('sub_category_name'),
        asset_category=asset_category
    )
    asset_type, _ = AssetType.objects.get_or_create(
        asset_type=validated_data.get('asset_type'),
        asset_sub_category=asset_sub_category
    )
    make_label_value = validated_data.get('make_label')
    if make_label_value:
        asset_make, _ = AssetMake.objects.get_or_create(
            make_label=validated_data.get('make_label'),
            asset_type=asset_type
        )
    else:
        return
    model_number_value = validated_data.get('model_number')
    if model_number_value:
        asset_model_number, _ = AssetModelNumber.objects.get_or_create(
            model_number=model_number_value,
            make_label=asset_make
        )
    else:
        return
    asset_spec, _ = AssetSpecs.objects.get_or_create(
        memory=validated_data.get('memory'),
        storage=validated_data.get('storage'),
        processor_speed=validated_data.get('processor_speed'),
        year_of_manufacture=validated_data.get('year_of_manufacture')
    )

    try:
        asset_code = validated_data.get('asset_code')
        asset_serial_number = validated_data.get('serial_number')
        if asset_code:
            Asset.objects.create(
                asset_code=validated_data.get('asset_code'),
                model_number=asset_model_number
            )
        elif asset_serial_number:
            Asset.objects.create(
                serial_number=asset_serial_number,
                model_number=asset_model_number
            )
        else:
            return
    except ValidationError:
        try:
            asset = Asset.objects.get(
                asset_code=validated_data.get('asset_code'),
                model_number=asset_model_number
            )
        except MultipleObjectsReturned:
            if isinstance(asset_model_number, CaseInsensitiveQuerySet):
                asset = Asset.objects.get(
                    asset_code=validated_data.get('asset_code'),
                    model_number=asset_model_number.first()
                )
            else:
                return
        except ObjectDoesNotExist:
            asset = Asset.objects.create(
                serial_number=asset_serial_number,
                model_number=asset_model_number
            )
        asset.serial_number = validated_data.get('serial_number')
        asset.verified = validated_data.get('verified') or True
        asset.current_status = validated_data.get('current_status') or ''

        try:
            user_email = email=validated_data.get('assigned_to')
            if user_email:
                User.objects.create(email=user_email)
        except IntegrityError:
            assigned_to = User.objects.get(
                email=user_email
            )
            asset.assigned_to = assigned_to.assetassignee

        asset.save()

        asset_condition, _ = AssetCondition.objects.get_or_create(
            asset=asset,
            notes=validated_data.get('notes') or ''
        )

    if asset and user_email:
        print(f'{asset} assigned to {user_email} has been saved succefully')



class Command(BaseCommand):
    help = 'Bulk create Assets from local or remote csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        validated_data_generator = load_data_from_local_csv(filepath)

        for valid_row in validated_data_generator:
            save_to_models(valid_row)
