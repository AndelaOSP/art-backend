import sys
import os
import csv
from tqdm import tqdm
import django

from import_util import is_valid_file, display_inserted, display_skipped

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import AssetType, AssetSubCategory   # noqa


def bulk_create_asset_types():
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
                sub_category_name = AssetSubCategory.objects.\
                    filter(sub_category_name=row['sub_category'])\
                    .exists()
                asset_type = AssetType.objects.filter(asset_type=row[
                    'asset_type']).exists()
                if not sub_category_name:
                    skipped[row['sub_category']] = [('Sub-Category {0} does '
                                                    'not exist'.format
                                                     (row['sub_category'])),
                                                    counter]
                elif asset_type:
                    skipped[row['asset_type']] = [(
                        'asset_type {0} already exists'.
                                                  format(row['asset_type'])),
                                                  counter]
                else:
                    asset = AssetType()
                    asset.asset_type = row['asset_type']
                    asset.asset_sub_category = AssetSubCategory.objects.\
                        get(sub_category_name=row['sub_category'])
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


if __name__ == '__main__':
    bulk_create_asset_types()
