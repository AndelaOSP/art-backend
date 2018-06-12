import sys
import os
import csv
from tqdm import tqdm
import django

from helpers import display_inserted, display_skipped

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import Asset, AssetModelNumber   # noqa


def bulk_create_asset():
    file_name = input('Enter the file name without extension:  ')
    print('\n')

    with open(file_name + '.csv', 'r', ) as f:
        file_length = len(f.readlines()) - 1
        f.seek(0)
        skipped = dict()
        inserted_records = []
        data = csv.DictReader(f, delimiter=',')
        counter = 1
        with tqdm(total=file_length) as pbar:
            for row in data:
                model_number = AssetModelNumber.objects.\
                    filter(model_number=row['model_number'])\
                    .exists()
                asset_code = Asset.objects.filter(asset_code=row[
                    'asset_code']).exists()
                serial_number = Asset.objects.filter(
                    serial_number=row['serial_number']).exists()
                if asset_code:
                    skipped[row['asset_code']] = [(
                        'asset_code {0} already exists'.
                                                  format(row['asset_code'])),
                                                  counter]
                elif serial_number:
                    skipped[row['serial_number']] = [
                        ('serial_number {0} already exists'.
                         format(row['serial_number'])), counter]
                elif not model_number:
                    skipped[row['model_number']] = [('model number {0} does '
                                                    'not exist'.format
                                                     (row['model_number'])),
                                                    counter]
                else:
                    asset = Asset()
                    asset.asset_code = row['asset_code']
                    asset.serial_number = row['serial_number']
                    asset.model_number = AssetModelNumber.objects.\
                        get(model_number=row['model_number'])
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records)
    display_skipped(skipped)


if __name__ == '__main__':
    bulk_create_asset()
