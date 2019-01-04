import random
import responses
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command

from core.models import AISUserSync
from core.tests import CoreBaseTestCase

User = get_user_model()


class UserSyncCommandsTestCase(CoreBaseTestCase):
    def setUp(self):
        self.ais_api_endpoint = 'http://ais_api.example.com'
        self.ais_users_endpoint = self.ais_api_endpoint + '/users'
        self.env_vars = {
            'AIS_LIMIT': '100',
            'AIS_URL': self.ais_api_endpoint,
            'AIS_TOKEN': 'testtoken',
            'RETRY_TIMEOUT': '1',
        }
        self.invalid_email = 'invalid email @email.com'
        self.sample_user_data = {
            'values': [
                {
                    'email': 'test.{}@email.com'.format(random.randint(1, 100)),
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'active',
                    'cohort': {
                        'name': 'Class 1 - NBO'
                    },
                    'location': {
                        'name': 'Nairobi'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
                {
                    'email': 'test.{}@email.com'.format(random.randint(1, 100)),
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'active',
                    'location': {
                        'name': 'Nairobi'
                    },
                    'cohort': {
                        'name': 'test'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
                {
                    'email': 'test.{}@email.com'.format(random.randint(1, 100)),
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'active',
                    'cohort': {
                        'name': 'Class 1 - NBO'
                    },
                    'location': {
                        'name': 'unknown'
                    },
                },
                {
                    'email': 'test.{}@email.com'.format(random.randint(1, 100)),
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'active',
                    'cohort': {
                        'name': 'Staff'
                    },
                    'location': {
                        'name': 'Lagos'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
                {
                    'email': 'test.{}@email.com'.format(random.randint(1, 100)),
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'suspended',
                    'cohort': {
                        'name': 'Class 1 - KLA'
                    },
                    'location': {
                        'name': 'Kampala'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
                {
                    'email': self.user.email,
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'suspended',
                    'cohort': {
                        'name': 'Class 1 - KLA'
                    },
                    'location': {
                        'name': 'Kampala'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
                {
                    'email': self.invalid_email,
                    'first_name': 'first1',
                    'last_name': 'last2',
                    'picture': 'https://test.example.com/pic/photo.jpg?sz=50',
                    'status': 'suspended',
                    'cohort': {
                        'name': 'Class 1 - KLA'
                    },
                    'location': {
                        'name': 'Kampala'
                    },
                    'updated_at': '2018-12-18T13: 30: 02.780Z',
                },
            ]
        }
        # a call to page 3 will return an empty result
        responses.add(
            responses.GET,
            self.ais_users_endpoint + '?limit={}&page=3'.format(self.env_vars['AIS_LIMIT']),
            json={},
        )

    def _confirm_call_count(self, expected_count, url=None):
        url = url or self.ais_users_endpoint
        call_count = len([resp.request.url for resp in responses.calls if url in resp.request.url])
        self.assertEqual(call_count, expected_count)

    @responses.activate
    def test_user_sync_with_missing_env_variables(self):
        "Test no call when env vars missing"
        user_count = User.objects.count()
        responses.add(responses.GET, self.ais_users_endpoint, json={})
        with patch.dict('os.environ', {'AIS_URL': '', 'AIS_TOKEN': ''}, clear=True):
            call_command('sync_users')
        self._confirm_call_count(0)
        # no change in user count
        self.assertEqual(user_count, User.objects.count())

    @responses.activate
    def test_failed_connection(self):
        "Test failed connection"
        user_count = User.objects.count()
        responses.add(responses.GET, self.ais_users_endpoint, status=404)
        with patch.dict('os.environ', self.env_vars, clear=True):
            call_command('sync_users')
        # +3 retries
        self._confirm_call_count(4)
        # no change in user count
        self.assertEqual(user_count, User.objects.count())

    @responses.activate
    def test_user_sync_valid_response(self):
        "Test valid response"
        user_count = User.objects.count()
        responses.add(responses.GET, self.ais_users_endpoint, json=self.sample_user_data)
        with patch.dict('os.environ', self.env_vars, clear=True):
            call_command('sync_users')
        # calls will exit at call number 3, since page 3 has empty result
        self._confirm_call_count(3)
        # additional users loaded to db
        self.assertGreater(User.objects.count(), user_count)
        # invalid emails not saved
        user_emails = [user.email for user in User.objects.all()]
        self.assertNotIn(self.invalid_email, user_emails)

    @responses.activate
    def test_user_sync_invalid_response(self):
        "Test invalid response"
        AISUserSync.objects.create()
        user_count = User.objects.count()
        responses.add(responses.GET, self.ais_users_endpoint, json=[])
        with patch.dict('os.environ', self.env_vars, clear=True):
            call_command('sync_users')
        # calls will exit at call number 3, since page 3 has empty result
        self._confirm_call_count(1)
        # no change in user count
        self.assertEqual(user_count, User.objects.count())
