# Standard Library
import os

# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from tqdm import tqdm

# App Imports
from core.models.asset import (
    Asset,
    AssetCategory,
    AssetCondition,
    AssetMake,
    AssetModelNumber,
    AssetSpecs,
    AssetStatus,
    AssetSubCategory,
    AssetType,
)
from tableschema import exceptions, Table, validate

User = get_user_model()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ASSET_DATA_FILE = os.path.join(BASE_PATH, 'assets.csv')

SCHEMA_FILE = os.path.join(BASE_PATH, 'schema.json')

SKIPPED_ASSETS_FILE = os.path.join(BASE_PATH, 'skipped.csv')


def write_skipped_assets(error, data=None):
    with open(SKIPPED_ASSETS_FILE, 'w') as output_file:
        output_file.write(f'{error} - {data}')


def load_data_from_local_csv(csv_file=ASSET_DATA_FILE):
    table = Table(csv_file, schema=SCHEMA_FILE)

    try:
        valid = validate(table.schema.descriptor)
        if valid:
            for keyed_row in table.iter(keyed=True):
                yield keyed_row
    except exceptions.ValidationError as exception:
        for error in exception.errors:
            print(error)
    except exceptions.CastError as exception:
        if not exception.errors:
            print(exception)

        for error in exception.errors:
            write_skipped_assets(error, [])
            # TODO: stream data from generator


def save_to_models(validated_data):
    asset_category, _ = AssetCategory.objects.get_or_create(
        name=validated_data.get('name')
    )
    asset_sub_category, _ = AssetSubCategory.objects.get_or_create(
        name=validated_data.get('name'), asset_category=asset_category
    )
    asset_type, _ = AssetType.objects.get_or_create(
        name=validated_data.get('name'), asset_sub_category=asset_sub_category
    )
    asset_make, _ = AssetMake.objects.get_or_create(
        asset_make=validated_data.get('asset_make'), asset_type=asset_type
    )
    asset_model_number, _ = AssetModelNumber.objects.get_or_create(
        model_number=validated_data.get('model_number'), asset_make=asset_make
    )
    asset_spec, _ = AssetSpecs.objects.get_or_create(
        memory=validated_data.get('memory'),
        storage=validated_data.get('storage'),
        processor_type=validated_data.get('processor_type'),
        year_of_manufacture=validated_data.get('year_of_manufacture'),
    )

    specified_serial_number = validated_data.get('serial_number')
    specified_asset_code = validated_data.get('asset_code')

    asset = Asset.objects.filter(model_number=asset_model_number)
    asset_code_filter = asset.filter(Q(asset_code=specified_asset_code))
    asset_serial_number_filter = asset.filter(Q(serial_number=specified_serial_number))
    if asset_code_filter.count() == 1:
        asset = asset_code_filter.first()
    elif asset_serial_number_filter.count() == 1:
        asset = asset_serial_number_filter.first()
    else:
        asset, _ = Asset.objects.get_or_create(
            asset_code=specified_asset_code,
            serial_number=specified_serial_number,
            model_number=asset_model_number,
        )

    asset.verified = not bool(validated_data.get('verified'))
    asset.save()

    specified_user_email = validated_data.get('email')

    if specified_user_email:
        asset_assigned_to, _ = User.objects.get_or_create(email=specified_user_email)
        asset.assigned_to = asset_assigned_to.assetassignee
        asset.save()

    asset_notes = validated_data.get('notes')
    if asset_notes:
        AssetCondition.objects.create(asset=asset, notes=asset_notes)
    specified_status = validated_data.get('current_status')
    if specified_status:
        AssetStatus.objects.create(asset=asset, current_status=specified_status)


class Command(BaseCommand):
    help = 'Bulk create Assets from local or remote csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        validated_data_generator = load_data_from_local_csv(filepath)
        # total=sum(1 for _ in validated_data_generator)

        with tqdm() as progress:
            for row_id, row_data in enumerate(validated_data_generator):
                progress.write(f'processing row number {row_id + 1}')
                save_to_models(row_data)
                progress.update()
