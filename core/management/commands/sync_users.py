# -*- coding: UTF-8 -*-
import logging
import os
import re
import requests
import time

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from django.utils.dateparse import parse_datetime

from core.management.commands import COMMAND_VERSION, DJANGO_VERSION
from core.models import AISUserSync, AndelaCentre
from core.slack_bot import SlackIntegration


logger = logging.getLogger(__name__)
User = get_user_model()
slack = SlackIntegration()

SYNC_SUCCESS = True
SYNC_ERRORS = set()


def fetch_ais_user_data(ais_url, ais_token, params):  # noqa: C901
    global SYNC_SUCCESS
    headers = {'api-token': ais_token}
    if not ais_url.endswith('/'):
        ais_url += '/'
    ais_url += 'users'
    logger.warning('Fetching data from AIS: {}'.format(ais_url))
    fetching_users = True
    ais_user_data = []
    page_num = params.get('page') or 1
    retries = 3
    retry_timeout = os.getenv('RETRY_TIMEOUT') or 5
    while fetching_users:
        params['page'] = page_num
        logger.warning('Params: {}'.format(params))
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
                    logger.warning('No data on page {}'.format(page_num))
                    fetching_users = False
            page_num += 1
        else:
            logger.error(
                'Unable to connect to AIS: {} : {} : {}. Retrying in 5 seconds'.format(
                    response.status_code, response.reason, response.text
                )
            )
            time.sleep(int(retry_timeout))
            retries -= 1
            if retries < 0:
                logger.error('Unable to connect to AIS. Exiting after 3 retries')
                fetching_users = False
                SYNC_SUCCESS = False
    return ais_user_data


def load_users_to_art(ais_user_data, current_sync_id=None):  # noqa: C901
    global SYNC_SUCCESS
    global SYNC_ERRORS
    last_run = None
    new_records = 0
    updated_records = 0
    logger.warning('Loading data to ART')
    try:
        last_run = AISUserSync.objects.exclude(id=current_sync_id).latest('created_at')
    except Exception as e:
        logger.error(str(e))
    if last_run:
        logger.warning('Last run: {}'.format(str(last_run)))
    total_num = len(ais_user_data)
    num = 0
    for ais_user in ais_user_data:
        num += 1
        print('Processing: **{}** of **{}**'.format(num, total_num))
        email = ais_user.get('email')
        updated_at = ais_user.get('updated_at')
        if updated_at:
            updated_at = parse_datetime(updated_at)
        try:
            validate_email(email)
        except Exception:
            if not last_run or (last_run and updated_at and updated_at > last_run.created_at):
                SYNC_ERRORS.add('Invalid Email')
                SYNC_SUCCESS = False
            continue
        try:
            user, user_created = User.objects.get_or_create(email=email)
        except Exception as e:
            logger.error(str(e))
            SYNC_ERRORS.add(str(e))
            SYNC_SUCCESS = False
            continue

        if (not user_created) and last_run and updated_at and updated_at < last_run.created_at:
            # if record has not been updated on AIS
            continue
        cohort_no = None
        andela_center = None
        location = ais_user.get('location')
        cohort = ais_user.get('cohort')
        picture = ais_user.get('picture').replace('?sz=50', '')
        user_status = ais_user.get('status')
        if location:
            location_name = location.get('name')
            try:
                andela_center, location_created = AndelaCentre.objects.get_or_create(
                    centre_name=location_name,
                )
                if location_created:
                    logger.warning('New location added: {}'.format(location_name))
            except Exception as e:
                logger.error(str(e))
        if cohort:
            cohort_name = cohort.get('name')
            if cohort_name.lower() == 'staff':
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
            logger.warning('Additional data for new user.')
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
            if picture and user.picture != picture:
                user.picture = picture
                modified = True
            if cohort_no and user.cohort != cohort_no:
                user.cohort = cohort_no
                modified = True
            if andela_center and user.location != andela_center:
                user.location = andela_center
                modified = True
            if user_status == 'suspended' and user.is_active:
                user.is_active = False
                modified = True

            if modified:
                logger.warning('Existing user modified. Updating')
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
        global SYNC_ERRORS
        new_records = 0
        updated_records = 0
        start_time = time.time()
        sync_record = AISUserSync.objects.create(running=True)
        ais_url = os.getenv('AIS_URL')
        ais_token = os.getenv('AIS_TOKEN')
        limit_per_page = os.getenv('AIS_LIMIT', 5000)
        if ais_url and ais_token:
            params = {'limit': limit_per_page, 'page': 1}
            ais_user_data = fetch_ais_user_data(ais_url, ais_token, params)
            logger.warning('{} records fetched'.format(len(ais_user_data)))
            if ais_user_data:
                new_records, updated_records = load_users_to_art(ais_user_data, current_sync_id=sync_record.id)
                sync_record.new_records = new_records
                sync_record.updated_records = updated_records
                logger.warning('Done. {} records added. {} records updated.'.format(new_records, updated_records))
        else:
            logger.error('Missing url or token.')
            SYNC_SUCCESS = False
        duration = time.time() - start_time
        running_time = timedelta(seconds=duration)

        sync_record.running_time = running_time
        sync_record.successful = SYNC_SUCCESS
        sync_record.running = False
        if SYNC_ERRORS:
            sync_record.message = ' '.join(SYNC_ERRORS)
        sync_record.save()
        message = 'User sync complete - {}'.format(str(sync_record))
        art_builds_channel = os.getenv('ART_BUILDS_CHANNEL') or '#art-builds'
        slack.send_message(message, channel=art_builds_channel)
