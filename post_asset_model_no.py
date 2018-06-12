import sys
import os
import csv
from tqdm import tqdm
import django

from import_util import display_inserted, display_skipped, is_valid_file

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import AssetModelNumber, AssetMake   # noqa


def bulk_create_asset_model_no():
    file_name = input('Enter the file name without extension:  ')
    print('\n')

    is_valid = is_valid_file(file_name)
    if not is_valid:
        return

    with open(file_name + '.csv', 'r', ) as f:
        file_length = len(f.readlines()) - 1
        f.seek(0)
        skipped = dict()
        inserted_records = []
        data = csv.DictReader(f, delimiter=',')
        counter = 1
        with tqdm(total=file_length) as pbar:
            for row in data:
                asset_model_no = AssetModelNumber.objects.\
                    filter(model_number=row['model_number'])\
                    .exists()
                asset_make = AssetMake.objects.filter(make_label=row[
                    'asset_make']).exists()

                if asset_model_no:
                    skipped[row['make_label']] = [(
                        'asset_model_no {0} already exists'.
                                                  format(row['model_number'])),
                                                  counter]
                elif not asset_make:
                    skipped[row['asset_make']] = [
                        ('asset make {0} does not exist'.
                         format(row['asset_make'])), counter]

                else:
                    new_asset_model_no = AssetModelNumber()
                    new_asset_model_no.model_number = row['model_number']
                    new_asset_model_no.make_label = AssetMake.objects.get(
                        make_label=row['asset_make']
                    )
                    new_asset_model_no.save()
                    inserted_records.append([new_asset_model_no, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


if __name__ == '__main__':
    bulk_create_asset_model_no()
