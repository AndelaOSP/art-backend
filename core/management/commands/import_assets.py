# -*- coding: UTF-8 -*-
import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tableschema import Table, validate, exceptions

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


def load_data_from_local_csv(filename=DATA_FILE):
    table = Table(filename, schema=SCHEMA_PATH)

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
    assigned_to, _ = User.objects.get_or_create(
        email=validated_data.get('assigned_to')
    )
    asset = Asset.objects.get_or_create(
        asset_code=validated_data.get('asset_code'),
        serial_number=validated_data.get('serial_number'),
        assigned_to=assigned_to.asset_assignee,
        verified=validated_data.get('verified')
    )
    asset_status, _ = AssetStatus.objects.get_or_create(
        asset=asset,
        current_status=validated_data.get('current_status')
    )
    asset_spec, _ = AssetSpecs.objects.get_or_create(
        memory=validated_data.get('memory'),
        storage=validated_data.get('storage'),
        processor_speed=validated_data.get('processor_speed'),
        year_of_manufacture=validated_data.get('year_of_manufacture')
    )

    asset_condition, _ = AssetCondition.objects.get_or_create(
        asset=asset,
        notes=validated_data.get('notes')
    )



class Command(BaseCommand):
    help = 'Bulk create Assets from local or remote csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        validated_row = load_data_from_local_csv()
        save_to_models(next(validated_row))
