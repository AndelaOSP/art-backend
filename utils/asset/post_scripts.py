import sys
import os
import csv
from tqdm import tqdm
import django

from utils.seed_bootstrap import collection_bootstrap

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
file_path = sys.path[-1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.asset import (
    AssetType,
    AssetMake,
    Asset,
    AssetModelNumber,
    AssetCategory,
    AssetSubCategory,
)  # noqa

skipped_rows = []


def write_skipped_records(records):
    """
    Write skipped record to a file
    :param record: record  that was skipped
    :param file_path: path to the output file
    :return: None
    """
    filename = "/skipped.csv"
    fieldnames = ('Row', 'Make', 'Type', 'Asset Code', 'Category',
                  'Sub-Category', 'Model Number', 'Serial No.', 'Error')
    with open(file_path + filename, "w") as csv_file:
        print('\n')
        dw = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)
        dw.writeheader()
        for row in records:
            dw.writerow(row)


def post_data(file):
    file_length = len(file.readlines()) - 1
    file.seek(0)
    data = csv.DictReader(file, delimiter=',')
    with tqdm(total=file_length) as progress:
        row_count = 0
        for row in data:
            progress.update(1)
            row_count += 1
            category_value = row.get('Category').strip()
            subcategory_value = row.get('Sub-Category').strip()
            type_value = row.get('Type').strip()
            make_value = row.get('Make').strip()
            modelnumber_value = row.get('Model Number').strip()
            assetcode_value = row.get('Asset Code').strip()
            serialnumber_value = row.get('Serial No.').strip()

            category_object, success = collection_bootstrap(
                AssetCategory, category_name=category_value)
            if success:
                subcategory_fields = {'sub_category_name': subcategory_value}
                subcategory_object, success = collection_bootstrap(
                    AssetSubCategory,
                    parent={'asset_category': category_object},
                    **subcategory_fields)
            else:
                row['Error'] = category_object
                row['Row'] = row_count
                skipped_rows.append(row)
                continue

            if success:
                type_fields = {'asset_type': type_value}
                type_object, success = collection_bootstrap(
                    AssetType,
                    parent={'asset_sub_category': subcategory_object},
                    **type_fields)
            else:
                row['Error'] = subcategory_object
                row['Row'] = row_count
                skipped_rows.append(row)
                continue

            if success:
                make_fields = {'make_label': make_value}
                make_object, success = collection_bootstrap(
                    AssetMake,
                    parent={'asset_type': type_object},
                    **make_fields)
            else:
                row['Error'] = type_object
                row['Row'] = row_count
                skipped_rows.append(row)
                continue

            if success:
                modelnumber_fields = {'model_number': modelnumber_value}
                modelnumber_object, success = collection_bootstrap(
                    AssetModelNumber,
                    parent={'make_label': make_object},
                    **modelnumber_fields)
            else:
                row['Error'] = make_object
                row['Row'] = row_count
                skipped_rows.append(row)
                continue

            if success:
                asset_fields = {
                    'asset_code': assetcode_value,
                    'serial_number': serialnumber_value
                }
                asset_object, success = collection_bootstrap(
                    Asset,
                    parent={'model_number': modelnumber_object},
                    **asset_fields)
            else:
                row['Error'] = modelnumber_object
                row['Row'] = row_count
                skipped_rows.append(row)
                continue

            if not success:
                row['Error'] = asset_object
                row['Row'] = row_count
                skipped_rows.append(row)

        write_skipped_records(skipped_rows)
