import sys
import os

import django
import requests

project_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

from utils.helpers import (
    is_valid_file, get_csv_from_url, is_valid_url
)  # noqa

from utils.user.post_scripts import (
    post_users
)  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


def post_user_csv():
    filename_or_url = input('Enter csv filename '
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
        post_users(f, file_length, 'csv')


def post_user_url():
    endpoint = input('Enter url path : ').strip()
    auth_header = input('Enter Authorization header '
                        '(Bearer <Token> or Token <Token>) : ').strip()

    headers = {"Authorization": auth_header}
    try:
        data = requests.get(endpoint, headers=headers).json()
        post_users(data, len(data), 'url')
    except Exception:
        print('Input correct url and Authorization header.')


def option():
    user_input = input('Option\n 1. Import from csv\n '
                       '2. Import from url\n 3. Exit\n: ').strip()

    result = {
        1: post_user_csv,
        2: post_user_url,
        3: exit
    }
    try:
        result[int(user_input)]()
    except (KeyError, ValueError):
        print('Invalid Option. Please try again')
        option()


if __name__ == '__main__':
    option()
