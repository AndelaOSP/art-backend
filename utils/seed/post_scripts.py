import sys
import os
import csv
from tqdm import tqdm
import django

from .helpers import display_inserted, display_skipped

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import (
    AssetType, AssetMake, Asset, AssetModelNumber, AssetCategory, AssetSubCategory,
)   # noqa


def post_asset_make(data, file_length):
    """
    Bulk creates asset make
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            make_label = row.get('make_label', '').strip()
            asset_type = row.get('asset_type', '').strip()
            print('I reached asset makes')

            if not make_label:
                skipped[row['make_label']] = [
                    ('asset_make has no value'.
                    format(row['make_label'])), counter]

            elif not asset_type:
                skipped[row['asset_type']] = [
                        ('asset type {0} does not exist'.
                            format(row['asset_type'])), counter]

            else:
                asset_make = AssetMake.objects.\
                    filter(make_label=row['make_label'])\
                    .exists()
                asset_type = AssetType.objects.filter(asset_type=row[
                    'asset_type']).exists()

                if asset_make:
                    skipped[row['make_label']] = [(
                        'asset_make {0} already exists'.
                            format(row['make_label'])), counter]
                elif not asset_type:
                    skipped[row['asset_type']] = [
                        ('asset type {0} does not exist'.
                            format(row['asset_type'])), counter]

                else:
                    new_asset_make = AssetMake()
                    new_asset_make.make_label = row['make_label']
                    new_asset_make.asset_type = AssetType.objects.get(
                        asset_type=row['asset_type']
                    )
                    new_asset_make.save()
                    inserted_records.append([new_asset_make, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


def post_asset(f, file_length):
    """
    Bulk creates assets
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            model_number = row.get('model_number', '').strip()
            asset_code = row.get('asset_code', '').strip()
            serial_number = row.get('serial_number', '').strip()
            print('i have reached asset')

            if model_number and asset_code and serial_number:
                model_number_status = AssetModelNumber.objects.\
                    filter(model_number=model_number)\
                    .exists()
                asset_code_status = Asset.objects.filter(
                    asset_code=asset_code).exists()
                serial_number_status = Asset.objects.filter(
                    serial_number=serial_number).exists()
                if asset_code_status:
                    skipped[asset_code] = [(
                        'asset_code {0} already exists'.format(asset_code)),
                                                counter]
                elif serial_number_status:
                    skipped[serial_number] = [
                        ('serial_number {0} already exists'.format(serial_number)), counter]
                elif not model_number_status:
                    skipped[model_number] = [('model number {0} does not exist'
                    .format(model_number)),counter]
                else:
                    asset = Asset()
                    asset.asset_code = asset_code
                    asset.serial_number = serial_number
                    asset.model_number = AssetModelNumber.objects.\
                        get(model_number=model_number)
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


def post_asset_category(f, file_length):
    """
    Bulk creates asset category
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            assets_category = row.get('Category', '').strip()
            assets_sub_category = row.get('Sub Category', '').strip()
            print('asset category here', assets_category)
            print('asset sub category here', assets_sub_category)

            if assets_category:
                assets_category = AssetCategory.objects.\
                    filter(category_name=row['Category']).exists()
                assets_sub_category = AssetSubCategory.objects.\
                    filter(sub_category_name=row['Sub Category']).\
                    exists()
                if assets_category:
                    if assets_sub_category:
                        skipped[row['Category']] = [(
                            'Category {0} already exists'.
                            format(row['Category'])), counter]
                        skipped[row['Sub Category']] = [(
                            'Sub Category {0} already exists'.
                            format(row['Sub Category'])), counter]
                    else:
                        category = AssetCategory.objects.get(
                            category_name=row['Category']
                        )
                        assets_sub_category = AssetSubCategory.\
                            objects.create(
                                sub_category_name=row['Sub Category'],
                                asset_category=category
                            )
                        assets_sub_category.save()
                        inserted_records.append([
                            assets_sub_category,
                            counter]
                        )
                        skipped[row['Category']] = [(
                            'Category {0} already exists'.
                            format(row['Category'])), counter]

                elif not assets_category:
                    if assets_sub_category:
                        asset_category = AssetCategory.objects.create(
                            category_name=row['Category']
                        )
                        asset_category.save()
                        inserted_records.append([
                            asset_category,
                            counter]
                        )
                        skipped[row['Sub Category']] = [(
                            'Sub Category {0} already exists'.
                            format(row['Sub Category'])), counter]
                    else:
                        asset_category = AssetCategory.objects.create(
                            category_name=row['Category']
                        )
                        asset_category.save()
                        category = AssetCategory.objects.get(
                            category_name=row['Category']
                        )
                        sub_category = AssetSubCategory.objects.create(
                            sub_category_name=row['Sub Category'],
                            asset_category=category
                        )
                        sub_category.save()
                        inserted_records.append([
                            asset_category,
                            counter]
                        )
                        inserted_records.append([
                            sub_category,
                            counter]
                        )

            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


def post_asset_model_no(f, file_length):
    """
    Bulk creates asset model number
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            asset_make = row.get('asset_make', '')
            model_number = row.get('model_number', '')
            print('I reached asset model number')

            if asset_make and model_number:
                asset_model_no = AssetModelNumber.objects.\
                    filter(model_number=model_number)\
                    .exists()
                asset_make_status = AssetMake.objects.filter(
                    make_label=asset_make).exists()

                if asset_model_no:
                    skipped[row['make_label']] = [(
                        'asset_model_no {0} already exists'.
                            format(model_number)), counter
                        ]
                elif not asset_make_status:
                    skipped[asset_make] = [
                        ('asset make {0} does not exist'.
                        format(asset_make)), counter]

                else:
                    new_asset_model_no = AssetModelNumber()
                    new_asset_model_no.model_number = model_number
                    new_asset_model_no.make_label = AssetMake.objects.get(
                        make_label=asset_make
                    )
                    new_asset_model_no.save()
                    inserted_records.append([new_asset_model_no, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


def post_asset_types(f, file_length):
    """
    Bulk creates asset types
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            asset_type = row.get('asset_type', '').strip()
            sub_category = row.get('Sub Category', '').strip()
            print('I reached asset types')
            if asset_type and sub_category:
                sub_category_name = AssetSubCategory.objects.\
                    filter(sub_category_name=sub_category)\
                    .exists()
                asset_type = AssetType.objects.filter(
                    asset_type=asset_type
                ).exists()
                if not sub_category_name:
                    skipped[sub_category] = [('Sub Category {0} does '
                                                    'not exist'.format
                                                    (sub_category)),
                                                    counter]
                elif asset_type:
                    skipped[asset_type] = [(
                        'asset_type {0} already exists'.
                                                format(asset_type)),
                                                counter]
                else:
                    asset = AssetType()
                    asset.asset_type = asset_type
                    asset.asset_sub_category = AssetSubCategory.objects.\
                        get(sub_category_name=sub_category)
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)
