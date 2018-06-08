import sys
import os
import django
import pandas as pd

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.asset import AssetCategory, AssetSubCategory  # noqa


def create_category(x):
    filter_category = AssetCategory.objects.filter(category_name=x).exists()
    if filter_category:
        return 'Category exist'
    else:
        add_category = AssetCategory.objects.create(category_name=x)
        add_category.save()
        return 'Category created'


def create_subcategory(z):
    category, subcategory = z.split(',')[0], z.split(',')[1]
    filter_subcategory = AssetSubCategory.objects.filter(
        sub_category_name=subcategory).exists()
    if filter_subcategory:
        return 'Sub category exist'
    else:
        get_category = AssetCategory.objects.get(category_name=category)
        add_sub_category = AssetSubCategory.objects.create(
            sub_category_name=subcategory,
            asset_category=get_category
        )
        add_sub_category.save()
        return 'Sub category created'


def csv_file(file):
    if os.path.isfile(file):
        if not file.endswith('.csv'):
            return 'File not supported'
        else:
            rd_csv = pd.read_csv(file)

            def check_if_category_exist(x):
                return create_category(x)

            def check_if_sub_category_exist(y):
                return create_subcategory(y)

            rd_csv['Category Summary'] = (rd_csv.Category).\
                apply(check_if_category_exist)
            rd_csv['SubCategory'] = rd_csv.Category.apply(lambda x: x) \
                + ',' + rd_csv['Sub Category'].apply(lambda x: x)
            rd_csv['Subcategory Summary'] = rd_csv.SubCategory.apply(
                check_if_sub_category_exist)
            return rd_csv.drop('SubCategory', 1)
    return 'File not found'


if __name__ == '__main__':
    print('********* Import the csv file ********')
    input_file = input('Import the file: ')
    print(csv_file(input_file))
