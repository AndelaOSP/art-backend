import sys
import os
import argparse
import django

project_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

from utils.helpers import (
    is_valid_file, get_csv_from_url, is_valid_url
    )  # noqa

from utils.asset.post_scripts import (
    post_asset_make, post_asset_category,
    post_asset_model_no, post_asset, post_asset_types,
    post_asset_subcategory
)  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="seed_asset",
        description="""
        ------------------------------------------------------------------------
        CSV file import script for Andela Resource Tracker (ART).
        ------------------------------------------------------------------------
        Running this program displays the following message expecting an input

        "Enter csv filename (without .csv or url link to csv): "

        Expected inputs:
        - A csv file without extension. Eg. 'assets', not 'asset.csv'
        - A URL pointing to a valid csv. Eg. 'http://link-to-csv.com/asset.csv'

        Expected columns/fields in input csv file:

        'Make', 'Type', 'Asset Code', 'Category', 'Sub-Category',
        'Model Number', 'Serial No.'

        without single quotation mark ''.

        Note: This program only supports .csv files or file format, it does
            not support other file formats.
        """
    )
    args = parser.parse_args()
    parser.print_help()

    filename_or_url = input('\n\nEnter csv filename '
                            '(without .csv or url link to csv): ').strip()
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/'  # noqa
    filename = ''

    if is_valid_url(filename_or_url):
        csvfile = get_csv_from_url(filename_or_url, filepath)
        filename = csvfile if csvfile else sys.exit()

    elif is_valid_file(filename_or_url):
        filename = filename_or_url + ".csv"

    else:
        sys.exit()

    with open(filepath + filename, 'r', ) as f:
        file_length = len(f.readlines()) - 1
        f.seek(0)

        # seed scripts
        post_asset_category(f, file_length)
        post_asset_subcategory(f, file_length)
        post_asset_types(f, file_length)
        post_asset_make(f, file_length)
        post_asset_model_no(f, file_length)
        post_asset(f, file_length)
