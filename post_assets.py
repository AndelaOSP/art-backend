import sys
import os
import csv
import django
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
django.setup()
from core.models.asset import Asset, AssetModelNumber


def bulk_create_asset():
    result = dict()
    error = dict()
    with open('assets.csv', 'r', ) as f:
        error['detail'] = []
        skipped_records = []
        inserted_records = []
        data = csv.DictReader(f, delimiter='|')
        for row in data:
            model_number = AssetModelNumber.objects.\
                filter(pk=row['model_number'])\
                .exists()
            asset_code = Asset.objects.filter(asset_code=row['asset_code'])\
                .exists()
            serial_number = Asset.objects.filter(
                serial_number=row['serial_number']).exists()
            if asset_code:
                skipped_records.append(row)
                error['detail'].append('asset_code {0} already exist'.
                                       format(row['asset_code']))
            elif serial_number:
                skipped_records.append(row)
                error['detail'].append('serial_number {0} already exist'.
                                       format(row['serial_number']))
                # raise ValidationError(_('asset_code and (or) serial'
                #                         ' number already exist '))
            elif not model_number:
                skipped_records.append(row)
                error['detail'].append('model number {0} does not exist'.
                                       format(row['model_number']))
            else:
                asset = Asset()
                asset.asset_code = row['asset_code']
                asset.serial_number = row['serial_number']
                asset.model_number = AssetModelNumber.objects.\
                    get(pk=row['model_number'])
                asset.save()
                inserted_records.append(asset)
    result['inserted_records'] = inserted_records
    result['skipped_records'] = skipped_records
    return result, error


if __name__ == '__main__':
    print(bulk_create_asset())
