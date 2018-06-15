import sys
import os
import csv
from django.utils import timezone

# from tqdm import tqdm
import django
# from utils.seed.helpers import DependencyChecker



# from helpers import display_inserted, display_skipped
class DependencyChecker():
    def __init__(self, columns):
        self.columns = columns

    @classmethod
    def check_dependency(cls, column, columns):
        instance = cls(columns)
        return instance.get_dependency(column)

    @classmethod
    def has_dep(cls, column, columns):
        instance = cls(columns)
        return instance.has_dep(column)

    def has_dep(self, column):
        if self.columns[0] == column:
            return False
        return True

    def get_dependency(self, column):
        if column in self.columns:
            colunm_index = self.columns.index(column)
            if colunm_index > 0:
                return self.columns[colunm_index - 1]
        return None


project_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.asset import (
    AssetCategory, AssetType,
    AssetSubCategory,
    Asset,
    AssetMake,
    AssetLog,
    AssetStatus,
    AssetCondition,
    AssetModelNumber,
    AllocationHistory,
    AssetIncidentReport,
) # noqa

# print(os.getcwd())
filepath = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# print(filepath)
with open(filepath + "/sample_csv/sample.csv", 'r', ) as f:
    file_length = len(f.readlines()) - 1
    f.seek(0)
    skipped = dict()
    inserted_records = []
    data = csv.DictReader(f, delimiter=',')
    for row in data:
        category, status = AssetCategory.objects.get_or_create(
            category_name=row['Category'])

        asset_sub_category, status = AssetSubCategory.objects.get_or_create(
            sub_category_name=row['Sub-category'],
            asset_category=category
        )

        asset_type, _ = AssetType.objects.get_or_create(
            asset_type=row['Type'],
            asset_sub_category=asset_sub_category
        )

        make_label, y = AssetMake.objects.get_or_create(
            make_label=row['Make'],
            asset_type=asset_type
        )

        asset_model_number, z = AssetModelNumber.objects.get_or_create(
            make_label=make_label,
            model_number=row['Model']
        )

        asset, z = Asset.objects.get_or_create(
            serial_number=row['Item'],
            asset_code=str(timezone.now()),
            model_number=asset_model_number
        )