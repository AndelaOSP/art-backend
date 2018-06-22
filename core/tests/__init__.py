from django.test import TestCase
from unittest.mock import patch

from core.slack_bot import SlackIntegration

class CoreBaseTestCase(TestCase):
    def setUp(self):
        self.patch_slack_id = patch.object(SlackIntegration, 'get_user_slack_id')
        self.patch_send_message = patch.object(SlackIntegration, 'send_message')

        self.patch_slack_id.return_value = 'test_id'
        self.patch_send_message.return_value = ''
        self.patch_slack_id.start()
        self.patch_send_message.start()

    def tearDown(self):
        self.patch_slack_id.stop()
        self.patch_send_message.stop()