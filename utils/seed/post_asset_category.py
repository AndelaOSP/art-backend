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

from core.models.asset import AssetCategory, AssetSubCategory  # noqa


def load_csv_file(file_name):  # noqa
    print('\n')
    if os.path.isfile(file_name):
        if not file_name.endswith('.csv'):
            return 'File not supported'

        else:
            with open(file_name, 'r', ) as f:
                file_length = len(f.readlines()) - 1
                f.seek(0)
                skipped = dict()
                inserted_records = []
                data = csv.DictReader(f, delimiter=',')
                counter = 1
                with tqdm(total=file_length) as pbar:
                    for row in data:
                        assets_category = AssetCategory.objects.\
                            filter(category_name=row['Category']).exists()
                        assets_sub_category = AssetSubCategory.objects.\
                            filter(sub_category_name=row['Sub Category']).\
                            exists()
                        if assets_category:
                            if assets_sub_category:
                                skipped[row['Category']] = [(
                                    'Category {0} already exists'.
                                    format(row['Category'])), counter]
                                skipped[row['Sub Category']] = [(
                                    'Sub Category {0} already exists'.
                                    format(row['Sub Category'])), counter]
                            else:
                                category = AssetCategory.objects.get(
                                    category_name=row['Category']
                                )
                                assets_sub_category = AssetSubCategory.\
                                    objects.create(
                                        sub_category_name=row['Sub Category'],
                                        asset_category=category
                                    )
                                assets_sub_category.save()
                                inserted_records.append([
                                    assets_sub_category,
                                    counter]
                                )
                                skipped[row['Category']] = [(
                                    'Category {0} already exists'.
                                    format(row['Category'])), counter]

                        elif not assets_category:
                            if assets_sub_category:
                                asset_category = AssetCategory.objects.create(
                                    category_name=row['Category']
                                )
                                asset_category.save()
                                inserted_records.append([
                                    asset_category,
                                    counter]
                                )
                                skipped[row['Sub Category']] = [(
                                    'Sub Category {0} already exists'.
                                    format(row['Sub Category'])), counter]
                            else:
                                asset_category = AssetCategory.objects.create(
                                    category_name=row['Category']
                                )
                                asset_category.save()
                                category = AssetCategory.objects.get(
                                    category_name=row['Category']
                                )
                                sub_category = AssetSubCategory.objects.create(
                                    sub_category_name=row['Sub Category'],
                                    asset_category=category
                                )
                                sub_category.save()
                                inserted_records.append([
                                    asset_category,
                                    counter]
                                )
                                inserted_records.append([
                                    sub_category,
                                    counter]
                                )

                        counter += 1
                        pbar.update(1)
            print("\n")
            display_inserted(inserted_records)
            display_skipped(skipped)

    return 'File not found'


if __name__ == '__main__':
    print('********* Import the csv file ********')
    input_file = input('Import the file: ')
    load_csv_file(input_file)  # noqa
    