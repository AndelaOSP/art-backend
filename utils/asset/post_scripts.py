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

skipped_rows = []


def write_skipped_records(records):
    filename = "/skipped.csv"
    fieldnames = ('Row', 'Make', 'Type', 'Asset Code', 'Category',
                  'Sub-Category', 'Model Number', 'Serial No.', 'Error')
    with open(file_path + filename, "w") as csv_file:
        print("Writing {} skipped rows to {}".format(len(records), filename))
        dw = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)
        dw.writeheader()
        for row in records:
            dw.writerow(row)


def record_errors(row, row_count, object_error):
    for line in skipped_rows:
        if line.get('Row') == row_count:
            line['Error'] += object_error
            return
    row['Error'] = object_error
    row['Row'] = row_count
    skipped_rows.append(row)


def create_object(collection, parent=None, row=None, row_count=None, **values):
    obj, success = collection_bootstrap(collection, parent, **values)
    if success:
        return obj
    record_errors(row, row_count, obj)


def post_data(file):
    file_length = len(file.readlines()) - 1
    file.seek(0)
    data = csv.DictReader(file, delimiter=',')
    with tqdm(total=file_length) as progress:
        row_count = 0
        for row in data:
            row_count += 1
            row_data = {'row': row, 'row_count': row_count}
            progress.write('Processing row {} of {}'.format(
                row_count, file_length))
            progress.update()
            category_value = row.get('Category').strip()
            category = create_object(
                'AssetCategory', category_name=category_value,
                **row_data)

            subcategory_value = row.get('Sub-Category').strip()
            subcategory = create_object(
                'AssetSubCategory',
                parent={'asset_category': category},
                sub_category_name=subcategory_value, **row_data)

            type_value = row.get('Type').strip()
            asset_type = create_object(
                'AssetType', parent={'asset_sub_category': subcategory},
                asset_type=type_value, **row_data)

            make_value = row.get('Make').strip()
            asset_make = create_object(
                'AssetMake', parent={'asset_type': asset_type},
                make_label=make_value, **row_data)

            modelnumber_value = row.get('Model Number').strip()
            asset_model_no = create_object(
                'AssetModelNumber', parent={'make_label': asset_make},
                model_number=modelnumber_value, **row_data)

            assetcode_value = row.get('Asset Code').strip() or None
            serialnumber_value = row.get('Serial No.').strip() or None

            asset_fields = {
                'asset_code': assetcode_value,
                'serial_number': serialnumber_value
            }
            asset_model_no = create_object(
                'Asset', parent={'model_number': asset_model_no},
                **row_data, **asset_fields)

    write_skipped_records(skipped_rows)
