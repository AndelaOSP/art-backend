import os
from django.test import TestCase
from core.models.asset import (AssetType, AssetSubCategory, AssetCategory,
                               AssetMake, AssetModelNumber, Asset)
# from utils.asset.post_scripts import post_asset_types, post_asset_subcategory
from utils.asset.post_scripts import post_data
from django.conf import settings

from utils.seed_bootstrap import collection_bootstrap


class TestPostScript(TestCase):
    """
    Contains tests for the asset type post scripts module
    """

    def setUp(self):
        self.csv_file = os.path.join(settings.BASE_DIR, 'utils/sample.csv')
        self.skipped_records = os.path.join(settings.BASE_DIR,
                                            'utils/skipped.csv')

    def test_bootstrap_creates_object_with_parent(self):
        count_before = AssetSubCategory.objects.count()
        parent_category = AssetCategory.objects.create(
            category_name='test category')
        sub_category_fields = {'sub_category_name': 'test subcategory'}
        parent = {'asset_category': parent_category}
        collection_bootstrap(
            'AssetSubCategory', parent=parent, **sub_category_fields)
        collection_bootstrap(
            'AssetSubCategory', parent=parent, **sub_category_fields)

        count_after = AssetSubCategory.objects.count()

        self.assertEqual(count_after, count_before + 1)

    def test_bootstrap_does_not_create_existing_object_with_different_parent(
            self):
        count_before = AssetSubCategory.objects.count()
        parent_category = AssetCategory.objects.create(
            category_name='test category')
        sub_category_fields = {'sub_category_name': 'test subcategory'}
        parent = {'asset_category': parent_category}
        collection_bootstrap('AssetSubCategory', parent, **sub_category_fields)

        different_category = parent_category = AssetCategory.objects.create(
            category_name='different category')
        parent = {'asset_category': different_category}
        collection_bootstrap('AssetSubCategory', parent, **sub_category_fields)

        count_after = AssetSubCategory.objects.count()

        self.assertEqual(count_after, count_before + 1)

    def test_bootstrap_creates_object_without_parent(self):
        count_before = AssetCategory.objects.count()
        category_fields = {'category_name': 'test category'}
        collection_bootstrap('AssetCategory', **category_fields)
        collection_bootstrap('AssetCategory', **category_fields)

        count_after = AssetCategory.objects.count()

        self.assertEqual(count_after, count_before + 1)

    def test_create_categories_from_csv(self):
        with open(self.csv_file, 'r') as file:
            post_data(file)

        with open(self.skipped_records, 'r') as skipped:
            file_length = len(skipped.readlines()) - 1
            self.assertEqual(file_length, 18)

        category_count = AssetCategory.objects.count()
        self.assertEqual(category_count, 2)

        subcategory_count = AssetSubCategory.objects.count()
        self.assertEqual(subcategory_count, 6)

        asset_types = AssetType.objects.count()
        self.assertEqual(asset_types, 16)

        asset_makes = AssetMake.objects.count()
        self.assertEqual(asset_makes, 20)

        model_numbers = AssetModelNumber.objects.count()
        self.assertEqual(model_numbers, 25)

        assets = Asset.objects.count()
        self.assertEqual(assets, 79)
