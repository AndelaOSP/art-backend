# Using requests, get the json file
import os
import sys
import django
import re

import requests
from django.contrib.auth import get_user_model

url = "https://api-prod.andela.com/api/v1/users"

headers = {'Authorization': os.getenv('Bearer')}

response = requests.get(url, headers=headers)

# Go through json data save the data
os.chdir("..")
below_path = os.getcwd()
sys.path.append(below_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models import AndelaCentre, User  # NOQA

user = get_user_model()

vlst = list(response.json().values())

for value in vlst[0]:  # NOQA

    values = dict()
    values.update({'email': value.get('email')})

    cohort = value.get('cohort')
    cohort_num = None
    if cohort:
        if cohort.get('name').lower() == 'staff':
            cohort_num = 0
        else:
            cohort_num = int(re.search(r'\d+', cohort.get('name')).group())

    user, created = User.objects.get_or_create(email=values.get('email'))

    if not created:
        # check if picture, cohort or slack_handle have changed
        if user.picture != value.get('picture'):
            user.picture = value.get('picture')
        if user.cohort != cohort_num:
            user.cohort = cohort_num
        if user.slack_handle != value.get('slack'):
            user.slack_handle = value.get('slack')
        user.save()

        continue

    if value.get('location'):
        location = value.get('location').get('name')

        if AndelaCentre.objects.filter(centre_name=location).exists():
            andelaCenter = AndelaCentre.objects.get(centre_name=location)
            value['location'] = andelaCenter

    if cohort:
        values.update({'cohort': cohort_num})

    values.update({'slack_handle': value.get('slack')})
    values.update({'picture': value.get('picture')})
    values.update({'phone_number': value.get('phone_number')})
    values.update({'location': value.get('location')})

    user.objects.create_user(**values)
