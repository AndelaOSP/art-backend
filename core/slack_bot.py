import os
import logging
from slackclient import SlackClient


class SlackIntegration(object):
    """Slack Integration class"""

    def __init__(self):
        """set the slack token"""
        slack_token = os.getenv('SLACK_TOKEN')
        if slack_token:
            self.slack_client = SlackClient(slack_token)

    def get_user_slack_id(self, user):
        """Get the slack user ID using the user email"""
        if not user:
            return os.getenv('OPS_CHANNEL') or '#art-test'
        user_email = user.email
        response = self.slack_client.api_call("users.list")
        users = response.get("members")
        if users:
            user_id = [
                member.get('id') for member in users
                if member.get('profile').get('email') == user_email
            ]
        try:
            return user_id[0]
        except Exception:
            logging.info("User not found")
            return None

    def send_message(self, message, user=None):
        """Sends message to slack user or channel"""
        if hasattr(self, 'slack_client'):
            slack_id = self.get_user_slack_id(user)
            if not slack_id:
                message = 'The message *"{}"* to {} not sent'.format(
                    message, user.email)
            self.slack_client.api_call(
                "chat.postMessage",
                channel=slack_id,
                text=message,
                username='@art-bot',
                as_user=True,
                icon_emoji=':ninja:')
