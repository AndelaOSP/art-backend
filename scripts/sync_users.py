# Using requests, get the json file
import os
import sys
import django
import re

import requests
from django.contrib.auth import get_user_model

url = "https://api-prod.andela.com/api/v1/users"

headers = {'Authorization': os.getenv('TOKEN')}

response = requests.get(url, headers=headers)

# Go through json data save the data
os.chdir("..")
below_path = os.getcwd()
sys.path.append(below_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models import AndelaCentre  # NOQA

user = get_user_model()

vlst = list(response.json().values())

for value in vlst[0]:

    values = dict()
    values.update({'email': value.get('email')})

    if user.objects.filter(email=values.get('email')).exists():
        continue

    if value.get('location'):
        location = value.get('location').get('name')

        if AndelaCentre.objects.filter(centre_name=location).exists():
            andelaCenter = AndelaCentre.objects.get(centre_name=location)
        else:
            andelaCenter = AndelaCentre.objects.create(centre_name=location)

        value['location'] = andelaCenter

    cohort = value.get('cohort')
    if cohort:
        if cohort.get('name').lower() == 'staff':
            cohort_num = 0
        else:
            cohort_num = int(re.search(r'\d+', cohort.get('name')).group())
        values.update({'cohort': cohort_num})

    values.update({'slack_handle': value.get('slack')})
    values.update({'picture': value.get('picture')})
    values.update({'phone_number': value.get('phone_number')})
    values.update({'location': value.get('location')})

    user.objects.create_user(**values)
