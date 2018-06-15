import sys
import os
import csv

import django

project_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
sys.path.append(project_dir)

from utils.seed.helpers import is_valid_file
from utils.seed.post_scripts import (
    post_asset_make, post_asset_category,
    post_asset_model_no, post_asset, post_asset_types
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


if __name__ == '__main__':
    filename = input('Enter csv filename (without .csv): ').strip()
    filepath = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), 'sample_csv/')

    if is_valid_file(filename):
        with open(filepath + filename + ".csv", 'r', ) as f:
            file_length = len(f.readlines()) - 1
            f.seek(0)
            # skipped = dict()
            # inserted_records = []
            # data = csv.DictReader(f, delimiter=',')

            post_asset_category(f, file_length)
            # post_asset_types(f, file_length)
            post_asset_make(f, file_length)
            post_asset_model_no(f, file_length)
            post_asset(f, file_length)
