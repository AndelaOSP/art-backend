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
                  'Sub-Category', 'Model Number', 'Serial No.', 'Error',
                   'Status', 'Processor Type', 'YOM', 'Storage', 'Verified',
                   'Notes', 'Memory', 'Assigned To')
    with open(file_path + filename, "w") as csv_file:
        print("Writing {} skipped rows to {}".format(len(records), filename))
        dw = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)
        dw.writeheader()
        for row in records:
            row['Error'] = set(row['Error'])
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
            asset_verified_value = row.get('Verified').strip() or True
            if asset_verified_value == 'No':
                asset_verified_value = False



            asset_fields = {
                'asset_code': assetcode_value,
                'serial_number': serialnumber_value,
                'verified': asset_verified_value,
            }
            asset = create_object(
                'Asset',
                parent={
                    'model_number': asset_model_no,
                },
                **row_data,
                **asset_fields
            )

            assigned_to_email_value = row.get('Assigned To').strip() or None
            if assigned_to_email_value:
                asset_user = create_object(
                    'User',
                    email=assigned_to_email_value
                )

                asset_allocation = create_object(
                    'AllocationHistory',
                    parent={'asset': asset},
                    current_owner=asset_user.assetassignee,
                    **row_data)

            asset_status_value = row.get('Status').strip() or None
            if asset_status_value:
                asset_status = create_object(
                    'AssetStatus',
                    parent={'asset': asset},
                    current_status=asset_status_value,
                    **row_data)

            asset_condition_notes_value = row.get('Notes').strip() or None
            if asset_condition_notes_value:
                # import ipdb; ipdb.set_trace()
                asset_condition = create_object(
                    'AssetCondition',
                    parent={'asset': asset},
                    notes=asset_condition_notes_value,
                    **row_data)

            spec_memory_value = row.get('Memory').strip() or None
            spec_storage_value = row.get('Storage').strip() or None
            spec_processor_type_value = row.get('Processor Type').strip() or None
            spec_year_of_manufacture_value = row.get('YOM').strip() or None

            spec_data = spec_memory_value or spec_storage_value or spec_processor_type_value or spec_year_of_manufacture_value

            if spec_data:
                asset_spec = create_object(
                    'AssetSpecs',
                    memory=spec_memory_value,
                    storage=spec_storage_value,
                    processor_type=spec_processor_type_value,
                    year_of_manufacture=spec_year_of_manufacture_value,
                    **row_data)

    write_skipped_records(skipped_rows)
