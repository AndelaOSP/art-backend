import sys
import os
import csv
import django

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
django.setup()
from core.models.asset import Asset, AssetModelNumber   # noqa


def bulk_create_asset():
    with open('assets.csv', 'r', ) as f:
        skipped = dict()
        skipped_records = []
        inserted_records = []
        data = csv.DictReader(f, delimiter='|')
        for row in data:
            model_number = AssetModelNumber.objects.\
                filter(model_number=row['model_number'])\
                .exists()
            asset_code = Asset.objects.filter(asset_code=row['asset_code'])\
                .exists()
            serial_number = Asset.objects.filter(
                serial_number=row['serial_number']).exists()
            if asset_code:
                skipped_records.append(row)
                skipped[row['asset_code']] = ('asset_code {0} already exists'.
                                              format(row['asset_code']))
            elif serial_number:
                skipped_records.append(row)
                skipped[row['serial_number']] = ('serial_number {0} '
                                                 'already exists'.
                                                 format(row['serial_number']))
            elif not model_number:
                skipped_records.append(row)
                skipped[row['model_number']] = ('model number {0} does '
                                                'not exist'.format
                                                (row['model_number']))
            else:
                asset = Asset()
                asset.asset_code = row['asset_code']
                asset.serial_number = row['serial_number']
                asset.model_number = AssetModelNumber.objects.\
                    get(model_number=row['model_number'])
                asset.save()
                inserted_records.append(asset)
    display_inserted(inserted_records)
    display_skipped(skipped)


def display_inserted(result):
    print('***************************************************************\n')
    print("There are {0}  successfully inserted records\n".format(len(result)))
    print('===============================================================\n')
    if len(result) <= 0:
        print("No record was inserted\n")
    else:
        for item in result:
            print("\t\t{0}".format(item))


def display_skipped(result):
    print('***************************************************************\n')
    print("There are {0}  skipped records \n".format(len(result)))
    print('===============================================================\n')
    if len(result) <= 0:
        print("No record was skipped \n")
    else:
        for key, value in result.items():
            print("{0} : \t\t{1}".format(key, value))


if __name__ == '__main__':
    print(bulk_create_asset())
