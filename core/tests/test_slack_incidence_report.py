# Standard Library
import logging
from unittest.mock import ANY, patch

# Third-Party Imports
from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase

# App Imports
from core.models import AllocationHistory, Asset
from core.slack_bot import SlackIntegration

logging.disable(logging.ERROR)
User = get_user_model()


def side_effect_success(*args, **kwargs):
    resp = {"ok": True}

    if args[0] == 'users.info':
        resp = {
            "ok": True,
            "user": {
                "id": "someid",
                "team_id": "teamid",
                "name": "name",
                "deleted": False,
                "profile": {"email": "test@site.com"},
            },
        }
    return resp


class SlackIntegrationTestCase(TestCase):
    def setUp(self):
        self.env_vars = {'SLACK_TOKEN': 'testtoken', 'SLACK_LIMIT': '100'}
        self.user, _ = User.objects.get_or_create(
            email='test@site.com', cohort=10, slack_id='someid', password='devpassword'
        )
        self.user1, _ = User.objects.get_or_create(
            email='test1@site.com', cohort=10, password='devpassword'
        )
        self.user2, _ = User.objects.get_or_create(
            email='test2@site.com', cohort=10, password='devpassword'
        )
        category = apps.get_model('core', 'AssetCategory').objects.create(
            name="Computer"
        )
        asset_sub_category = apps.get_model('core', 'AssetSubCategory').objects.create(
            name="Computer Accessories", asset_category=category
        )
        asset_type = apps.get_model('core', 'AssetType').objects.create(
            name="Accessory", asset_sub_category=asset_sub_category
        )
        asset_make = apps.get_model('core', 'AssetMake').objects.create(
            name="Sades", asset_type=asset_type
        )
        self.asset_model = apps.get_model('core', 'AssetModelNumber').objects.create(
            name="12345", asset_make=asset_make
        )
        with patch.dict('os.environ', self.env_vars, clear=True):
            self.slack = SlackIntegration()

    @patch("core.slack_bot.SlackClient.api_call")
    def test_no_payload_no_assets(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        data = {'channel_id': 'some_value', 'user_id': 'some_value'}
        self.slack.send_incidence_report(data)
        self.assertEqual(fake_slack.call_count, 2)
        fake_slack.assert_any_call('users.info', user=ANY)
        fake_slack.assert_any_call(
            'chat.postEphemeral',
            username=ANY,
            channel=ANY,
            user=ANY,
            response_url=ANY,
            response_type=ANY,
            text=ANY,
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_no_payload_with_assets(self, fake_slack):
        asset = Asset.objects.create(
            asset_code="testIC002",
            serial_number="testSN0045",
            model_number=self.asset_model,
            purchase_date="2018-07-10",
        )
        AllocationHistory.objects.create(
            asset=asset, current_owner=self.user.assetassignee
        )
        fake_slack.side_effect = side_effect_success
        data = {'channel_id': 'some_value', 'user_id': 'some_value'}
        self.slack.send_incidence_report(data)
        fake_slack.assert_any_call('users.info', user=ANY)
        fake_slack.assert_any_call('dialog.open', trigger_id=ANY, dialog=ANY)
