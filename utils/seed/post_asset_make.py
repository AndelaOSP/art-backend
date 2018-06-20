import sys
import os
import csv
from tqdm import tqdm
import django

from helpers import display_inserted, display_skipped, is_valid_file

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import AssetType, AssetMake   # noqa


def bulk_create_asset():  # noqa
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
                make_label = row.get('make_label', None)
                asset_type = row.get('asset_type', None)

                if make_label is None:
                    skipped[row['make_label']] = [(
                            'asset_make has no value'.
                            format(row['make_label'])), counter]

                elif asset_type is None:
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


if __name__ == '__main__':
    bulk_create_asset()
