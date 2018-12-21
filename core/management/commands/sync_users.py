# -*- coding: UTF-8 -*-
import logging
import os
import re
import requests
import time

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.management.commands import COMMAND_VERSION, DJANGO_VERSION
from core.models import AISUserSync, AndelaCentre, KENYA, NIGERIA, RWANDA, UGANDA, EGYPT, USA, GHANA


logger = logging.getLogger(__name__)
User = get_user_model()

SYNC_SUCCESS = True
DEFAULT_COUNTRY_FOR_LOCATION = {
    'Accra': GHANA,
    'Cairo': EGYPT,
    'Kampala': UGANDA,
    'Kigali': RWANDA,
    'Lagos': NIGERIA,
    'Nairobi': KENYA,
    'New York': USA,
}


def fetch_ais_user_data(ais_url, ais_token, params):  # noqa: C901
    global SYNC_SUCCESS
    headers = {'api-token': ais_token}
    if not ais_url.endswith('/'):
        ais_url += '/'
    ais_url += 'users'
    logger.warn('Fetching data from AIS: {}'.format(ais_url))
    fetching_users = True
    ais_user_data = []
    page_num = 1
    retries = 3
    while fetching_users:
        params['page'] = page_num
        logger.warn('Params: {}'.format(params))
        response = requests.get(ais_url, params=params, headers=headers)
        if response.ok:
            try:
                fetched_users = response.json().get('values')
            except Exception as e:
                logger.error(str(e))
                fetching_users = False
                SYNC_SUCCESS = False
            else:
                if fetched_users:
                    ais_user_data += fetched_users
                else:
                    logger.warn('No data on page {}'.format(page_num))
                    fetching_users = False
        else:
            logger.error(
                'Unable to connect to AIS: {} : {} : {}. Retrying in 5 seconds'.format(
                    response.status_code, response.reason, response.text
                )
            )
            time.sleep(5)
            retries -= 1
            if retries <= 0:
                logger.error('Unable to connect to AIS. Exiting after 3 retries')
                fetching_users = False
                SYNC_SUCCESS = False
        page_num += 1
    return ais_user_data


def load_users_to_art(ais_user_data):  # noqa: C901
    global SYNC_SUCCESS
    last_run = None
    new_records = 0
    updated_records = 0
    logger.warn('Loading data to ART')
    try:
        last_run = AISUserSync.objects.latest('created_at')
    except Exception as e:
        logger.error(str(e))
    if last_run:
        logger.warn('Last run: {}'.format(str(last_run)))
    for ais_user in ais_user_data:
        email = ais_user.get('email')
        try:
            user, user_created = User.objects.get_or_create(email=email)
        except Exception as e:
            logger.error(str(e))
            SYNC_SUCCESS = False
            continue
        cohort_no = None
        andela_center = None
        location = ais_user.get('location')
        cohort = ais_user.get('cohort')
        picture = ais_user.get('picture').replace('?sz=50', '')
        user_status = ais_user.get('status')
        if location:
            location_name = location.get('name')
            country = DEFAULT_COUNTRY_FOR_LOCATION.get(location_name)
            try:
                andela_center, location_created = AndelaCentre.objects.get_or_create(
                    centre_name=location_name,
                    country=country,
                )
                if location_created:
                    logger.warn('New location added: {}'.format(location_name))
            except Exception as e:
                logger.error(str(e))
        if cohort:
            cohort_name = cohort.get('name')
            if cohort_name == 'Staff':
                cohort_no = 0
            else:
                try:
                    cohort_num_data = re.findall(r'(\d+)', cohort_name)
                except Exception as e:
                    logger.error(str(e))
                else:
                    if len(cohort_num_data) == 1:
                        cohort_no = int(cohort_num_data[0])
                    else:
                        logger.error('Unable to extract user cohort')
        if user_created:
            logger.warn('Additional data for new user.')
            user.first_name = ais_user.get('first_name')
            user.last_name = ais_user.get('last_name')
            user.picture = picture
            user.cohort = cohort_no
            user.location = andela_center
            if user_status == 'suspended':
                user.is_active = False

            user.save()
            new_records += 1
        else:
            # check if picture or cohort have changed
            modified = False
            if user.picture != picture:
                user.picture = picture
                modified = True
            if user.cohort != cohort_no:
                user.cohort = cohort_no
                modified = True
            if andela_center and user.location != andela_center:
                user.location = andela_center
                modified = True
            if user_status == 'suspended' and user.is_active:
                user.is_active = False
                modified = True

            if modified:
                logger.warn('Existing user modified. Updating')
                user.save()
                updated_records += 1
    return new_records, updated_records


class Command(BaseCommand):
    requires_system_checks = True
    requires_migrations_checks = True

    def get_version(self):
        """
        Return version (semver) of sync_users command
        """
        return f"sync_users v{COMMAND_VERSION}, Django v{DJANGO_VERSION}"

    def handle(self, *args, **options):
        global SYNC_SUCCESS
        new_records = 0
        updated_records = 0
        start_time = time.time()
        ais_url = os.getenv('AIS_URL')
        ais_token = os.getenv('AIS_TOKEN')
        limit_per_page = os.getenv('AIS_LIMIT', 5000)
        if ais_url and ais_token:
            params = {'limit': limit_per_page, 'page': 1}
            ais_user_data = fetch_ais_user_data(ais_url, ais_token, params)
            logger.warn('{} records fetched'.format(len(ais_user_data)))
            if ais_user_data:
                new_records, updated_records = load_users_to_art(ais_user_data)
                logger.warn('Done. {} records added. {} records updated.'.format(new_records, updated_records))
        else:
            logger.error('Missing url or token.')
            SYNC_SUCCESS = False
        duration = time.time() - start_time
        running_time = timedelta(seconds=duration)
        AISUserSync.objects.create(
            running_time=running_time,
            successful=SYNC_SUCCESS,
            new_records=new_records,
            updated_records=updated_records,
        )
