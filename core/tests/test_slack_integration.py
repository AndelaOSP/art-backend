# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from django.test import TestCase

# App Imports
from core.slack_bot import SlackIntegration

User = get_user_model()


def side_effect_success(*args, **kwargs):
    resp = {}
    if args[0] == 'chat.postMessage':
        resp = {
            "ok": True,
            "channel": kwargs.get('channel'),
            "ts": "1503435956.000247",
            "message": {"text": kwargs.get('text')},
        }
    elif args[0] == 'users.list':
        resp = {
            "ok": True,
            "members": [
                {
                    "id": "someid",
                    "team_id": "teamid",
                    "name": "name",
                    "deleted": False,
                    "profile": {"email": "slacktest@andela.com"},
                },
                {
                    "id": "anotherid",
                    "team_id": "teamid",
                    "name": "name1",
                    "deleted": False,
                    "profile": {"email": "slacktest1@andela.com"},
                },
            ],
            "response_metadata": {},
        }
    elif args[0] == 'users.info':
        resp = {
            "ok": True,
            "user": {
                "id": "someid",
                "team_id": "teamid",
                "name": "name",
                "deleted": False,
                "profile": {"email": "slacktest@andela.com"},
            },
        }
    return resp


def side_effect_multiple_users(*args, **kwargs):
    resp = {}
    if args[0] == 'users.list':
        resp = {
            "ok": True,
            "members": [
                {
                    "id": "someid",
                    "team_id": "teamid",
                    "name": "name",
                    "deleted": False,
                    "profile": {"email": "slacktest@andela.com"},
                },
                {
                    "id": "anotherid",
                    "team_id": "teamid",
                    "name": "name1",
                    "deleted": False,
                    "profile": {"email": "slacktest1@andela.com"},
                },
            ],
            "response_metadata": {"next_cursor": "some_key"},
        }
    return resp


def side_effect_failure(*args, **kwargs):
    resp = {"ok": False, "error": 'some_error'}
    return resp


class SlackIntegrationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env_vars = {
            'SLACK_TOKEN': 'testtoken',
            'SLACK_LIMIT': '100',
            'AIS_LIMIT': '100',
            'AIS_URL': '',
            'AIS_TOKEN': 'testtoken',
            'RETRY_TIMEOUT': '1',
            'RETRIES': '4',
            'PROJECT_ID': '',
            'PRIVATE_KEY': '',
            'CLIENT_EMAIL': '',
        }
        cls.patch_env = patch.dict('os.environ', cls.env_vars)
        cls.patch_firebase = patch('api.authentication.auth')

        cls.patch_env.start()
        cls.patch_firebase.start()

    def setUp(self):
        self.slack = SlackIntegration()
        self.user, _ = User.objects.get_or_create(
            email='slacktest@andela.com',
            cohort=10,
            slack_id='someid',
            password='devpassword',
        )
        self.user1, _ = User.objects.get_or_create(
            email='slacktest1@andela.com', cohort=10, password='devpassword'
        )
        self.user2, _ = User.objects.get_or_create(
            email='slacktest2@andela.com', cohort=10, password='devpassword'
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_to_specified_channel(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        self.slack.send_message('specified_channel', channel='#test-channel')
        fake_slack.assert_called_with(
            "chat.postMessage",
            channel='#test-channel',
            text='specified_channel',
            username='@art-bot',
            as_user=True,
            icon_emoji=':ninja:',
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_without_specified_channel(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        self.slack.send_message('without_specified_channel')
        fake_slack.assert_called_with(
            "chat.postMessage",
            channel='#art-test',
            text='without_specified_channel',
            username='@art-bot',
            as_user=True,
            icon_emoji=':ninja:',
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_with_ops_channel_set(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        with patch.dict('os.environ', {'OPS_CHANNEL': '#ops-channel'}, clear=True):
            self.slack.send_message('ops_channel_set')
        fake_slack.assert_called_with(
            "chat.postMessage",
            channel='#ops-channel',
            text='ops_channel_set',
            username='@art-bot',
            as_user=True,
            icon_emoji=':ninja:',
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_to_user_with_existing_slack_id(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        self.slack.send_message('existing_slack_id', user=self.user)

        # 2 calls for existing id - info and send message
        self.assertEqual(fake_slack.call_count, 2)
        fake_slack.assert_any_call('users.info', user=self.user.slack_id)
        fake_slack.assert_any_call(
            "chat.postMessage",
            channel=self.user.slack_id,
            text='existing_slack_id',
            username='@art-bot',
            as_user=True,
            icon_emoji=':ninja:',
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_to_user_without_existing_slack_id(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        self.slack.send_message('without_existing_slack_id', user=self.user1)

        # 2 calls for existing id - info and send message
        self.assertEqual(fake_slack.call_count, 2)
        fake_slack.assert_any_call('users.list', limit=self.env_vars.get('SLACK_LIMIT'))
        fake_slack.assert_any_call(
            "chat.postMessage",
            channel='anotherid',
            text='without_existing_slack_id',
            username='@art-bot',
            as_user=True,
            icon_emoji=':ninja:',
        )

        # after call slack id is saved to db
        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.slack_id, 'anotherid')

    @patch("core.slack_bot.SlackClient.api_call")
    def test_send_message_to_user_not_on_slack(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        resp = self.slack.send_message('not_on_slack', user=self.user2)
        self.assertEqual(fake_slack.call_count, 1)
        self.assertFalse(resp.get('ok'))

    @patch("core.slack_bot.SlackClient.api_call")
    def test_error_response(self, fake_slack):
        fake_slack.side_effect = side_effect_failure
        resp = self.slack.send_message('should error', user=self.user)
        self.assertFalse(resp.get('ok'))

    @patch("core.slack_bot.SlackClient.api_call")
    def test_max_slack_call_count(self, fake_slack):
        fake_slack.side_effect = side_effect_multiple_users
        resp = self.slack.send_message('should error', user=self.user2)
        self.assertFalse(resp.get('ok'))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.patch_env.stop()
        cls.patch_firebase.stop()
