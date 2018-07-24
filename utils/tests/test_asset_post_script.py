import os
from django.test import TestCase
from core.models.asset import AssetType, AssetSubCategory, AssetCategory
from utils.asset.post_scripts import post_asset_types, post_asset_subcategory
from django.conf import settings


class TestPostScript(TestCase):
  """
  Contains tests for the asset type post scripts module
  """
  def tearDown(self):
    AssetType.objects.all().delete()
    AssetSubCategory.objects.all().delete()
    AssetCategory.objects.all().delete()

  def setUp(self):
    self.csv_path = os.path.join(settings.BASE_DIR, 'utils/sample.csv')
    self.accessory_category = AssetCategory(category_name='Accessories')
    self.accessory_category.save()
    self.asset_sub_category = AssetSubCategory(sub_category_name='Computers',
      asset_category=self.accessory_category)
    self.asset_sub_category.save()

  def test_post_asset_types_that_it_creates_assets(self):
    with open(self.csv_path,'r') as file:
      post_asset_types(file, 96)
    asset_type = AssetType.objects.filter(asset_type='Windows PC'.title())
    self.assertTrue(asset_type.exists())

  def test_post_asset_types_doesnot_create_asset_if_no_sub_category(self):
    AssetSubCategory.objects.filter(sub_category_name=self.asset_sub_category.sub_category_name)\
      .delete()
    with open(self.csv_path,'r') as file:
      post_asset_types(file, 96)
    asset_type = AssetType.objects.filter(asset_type='Windows PC'.title())
    self.assertFalse(asset_type.exists())

  def test_post_asset_subcategory_create_asset_sub_category(self):
    AssetCategory.objects.create(category_name='Electronics')
    with open(self.csv_path,'r') as file:
      post_asset_subcategory(file, 96)
    asset_sub_category = AssetSubCategory.objects\
    .filter(sub_category_name='Electrical Accessories'.title())
    self.assertTrue(asset_sub_category.exists())
