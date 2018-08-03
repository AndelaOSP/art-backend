import sys
import os
import csv
from tqdm import tqdm
import django

from utils.helpers import display_inserted, display_skipped

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.user import (
    User
)  # noqa


def post_users(f, file_length, data_type):
    """
    Bulk creates asset make
    :param type: specifies type of import
    :param f: open csv file
    :param file_length: length of data
    :return:
    """
    skipped = dict()
    inserted_records = []
    counter = 1
    if data_type == 'csv':
        f.seek(0)
        data = csv.DictReader(f, delimiter=',')

    else:
        data = f

    with tqdm(total=file_length) as pbar:
        for row in data:
            email = row.get('email', '').strip()
            if User.objects.filter(email=email).exists():
                skipped[row['email']] = [
                    f"User {email} already exists", counter]
                continue
            user_attr = [
                'first_name', 'last_name', 'email',
                'cohort', 'picture', 'phone_number'
            ]
            user_data = dict()
            for attr in user_attr:
                user_data[attr] = row.get(attr)
            new_user = User.objects.create(**user_data)
            inserted_records.append([new_user, counter])
            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "USERS")
    display_skipped(skipped)
