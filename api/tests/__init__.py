import logging

from django.test import TestCase
from unittest.mock import patch

from core.slack_bot import SlackIntegration

logging.disable(logging.WARNING)


class APIBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patch_slack_id = patch.object(SlackIntegration, 'get_user_slack_id')
        cls.patch_send_message = patch.object(SlackIntegration, 'send_message')

        cls.patch_slack_id.return_value = 'test_id'
        cls.patch_send_message.return_value = ''
        cls.patch_slack_id.start()
        cls.patch_send_message.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.patch_slack_id.stop()
        cls.patch_send_message.stop()
