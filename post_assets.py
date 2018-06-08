import sys
import os
import csv
import django

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
django.setup()
from core.models.asset import Asset, AssetModelNumber   # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


def bulk_create_asset():
    file_name = input("Enter the file name without extension:  ")
    with open(file_name + '.csv', 'r', ) as f:
        skipped = dict()
        inserted_records = []
        data = csv.DictReader(f, delimiter=',')
        counter = 1
        for row in data:
            model_number = AssetModelNumber.objects.\
                filter(model_number=row['model_number'])\
                .exists()
            asset_code = Asset.objects.filter(asset_code=row['asset_code'])\
                .exists()
            serial_number = Asset.objects.filter(
                serial_number=row['serial_number']).exists()
            if asset_code:
                skipped[row['asset_code']] = [('asset_code {0} already exists'.
                                              format(row['asset_code'])),
                                              counter]
            elif serial_number:
                skipped[row['serial_number']] = [('serial_number {0} '
                                                 'already exists'.
                                                  format(row['serial_number']
                                                         )), counter]
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
    display_inserted(inserted_records)
    display_skipped(skipped)


def display_inserted(result):
    print('***************************************************************\n')
    print("There are {0}  successfully inserted records\n".format(len(result)))
    print('===============================================================\n')
    if len(result) <= 0:
        print("No record was inserted\n")
    else:
        print('{0} \t{1} \t '.format('Line No.', 'Description'))
        print('------------------------------------------------------------\n')
        for item in result:
            print('{0}\t{1}'.format(item[1], item[0]))


def display_skipped(result):
    print('***************************************************************\n')
    print('There are {0}  skipped records \n'.format(len(result)))
    print('===============================================================\n')
    if len(result) <= 0:
        print('No record was skipped \n')
    else:
        print('{0} \t{1} \t {2}'.format('Line No.', 'Description',
                                        'Error Message'))
        print('------------------------------------------------------------\n')
        for key, value in result.items():

            print('{0}\t \t{1} \t{2}'.format(value[1], key, value[0]))


if __name__ == '__main__':
    bulk_create_asset()
