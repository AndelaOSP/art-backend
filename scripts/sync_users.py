# Using requests, get the json file
import os

import requests


from django.contrib.auth import get_user_model

url = "https://api-prod.andela.com/api/v1/users"

headers = {'Authorization': os.getenv('TOKEN')}

response = requests.get(url, headers=headers)

# Go through json data save the data

user = get_user_model()

vlst = list(response.json().values())

for value in vlst[0]:
    user.create_user(**value)
    print(value)
