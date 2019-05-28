# Standard Library
import logging
from unittest.mock import ANY, patch

# Third-Party Imports
from django.contrib.auth import get_user_model

# App Imports
from core.models import AllocationHistory
from core.slack_bot import SlackIntegration
from core.tests import CoreBaseTestCase

logging.disable(logging.ERROR)
User = get_user_model()


def side_effect_success(*args, **kwargs):
    resp = {"ok": True}

    if args[0] == "users.info":
        resp = {
            "ok": True,
            "user": {
                "id": "someid",
                "team_id": "teamid",
                "name": "name",
                "deleted": False,
                "profile": {"email": "testslack@andela.com"},
            },
        }
    return resp


class SlackIntegrationTestCase(CoreBaseTestCase):
    def setUp(self):
        self.slack = SlackIntegration()

    @patch("core.slack_bot.SlackClient.api_call")
    def test_no_payload_no_assets(self, fake_slack):
        fake_slack.side_effect = side_effect_success
        data = {"channel_id": "some_value", "user_id": "some_value"}
        self.slack.send_incidence_report(data)
        self.assertEqual(fake_slack.call_count, 2)
        fake_slack.assert_any_call("users.info", user=ANY)
        fake_slack.assert_any_call(
            "chat.postEphemeral",
            username=ANY,
            channel=ANY,
            user=ANY,
            response_url=ANY,
            response_type=ANY,
            text=ANY,
        )

    @patch("core.slack_bot.SlackClient.api_call")
    def test_no_payload_with_assets(self, fake_slack):
        self.user.slack_id = "comeid"
        self.user.email = "testslack@andela.com"
        self.user.save()
        AllocationHistory.objects.create(
            asset=self.test_asset, current_assignee=self.user.assetassignee
        )
        fake_slack.side_effect = side_effect_success
        data = {"channel_id": "some_value", "user_id": "someid"}
        self.slack.send_incidence_report(data)
        fake_slack.assert_any_call("users.info", user=ANY)
        fake_slack.assert_any_call("dialog.open", trigger_id=ANY, dialog=ANY)
