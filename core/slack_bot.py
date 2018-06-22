import os
import logging
from slackclient import SlackClient


class SlackIntegration(object):
    """Slack Integration class"""

    def __init__(self):
        """set the slack token"""
        self.slack_client = SlackClient(os.getenv('SLACK_TOKEN'))

    def get_user_slack_id(self, user_email):
        """Get the slack user ID using the user email"""
        response = self.slack_client.api_call("users.list")
        users = response["members"]
        for user in users:
            try:
                slack_email = user.get('profile').get('email')
                if slack_email == user_email:
                    return user.get('id')
            except Exception:
                logging.info("User not found")

    def send_message(self, message, user=None):
        """Sends message to slack user or channel"""
        if user:
            slack_id = self.get_user_slack_id(user.email)
        else:
            slack_id = os.getenv('OPS_CHANNEL') or '#art-test'
        self.slack_client.api_call(
                "chat.postMessage",
                channel=slack_id,
                text=message,
                username='@art-bot',
                as_user=True,
                icon_emoji=':ninja:'
                )
