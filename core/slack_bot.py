import os
import json
import logging
from slackclient import SlackClient
from rest_framework import status
from rest_framework.response import Response


class SlackIntegration(object):
    """Slack Integration class"""

    def __init__(self):
        """set the slack token"""
        slack_token = os.getenv('SLACK_TOKEN')
        self.incidence_ts = {}
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

    def send_incidence_report(self, incidence_report, assets, token=None):
        """Sends incidence report from slack using a slash command"""

        if incidence_report.get('payload') is None:
            channel_id = incidence_report.get('channel_id')
            user_id = incidence_report.get('user_id')
            self.slack_client.api_call(
                "chat.postEphemeral",
                username='BoluBot',
                channel=channel_id,
                user=user_id,
                response_type='ephemeral',
                text="Would you like to log incident report?",
                attachments=[
                    {
                        "fallback": "You are unable to choose a game",
                        "callback_id": "choice_made",
                        "color": "#3AA3E3",
                        "attachment_type": "default",
                        "actions": [
                            {
                                "name": "game",
                                "text": "Yes",
                                "type": "button",
                                "value": "yes"
                            },
                            {
                                "name": "game",
                                "text": "No",
                                "type": "button",
                                "value": "no"
                            },
                        ]
                    }
                ]
            )
            return Response(status=status.HTTP_200_OK)

        payload = incidence_report.get('payload', None)
        payload = json.loads(payload)

        if payload['type'] == 'dialog_cancellation':
            return Response(status=status.HTTP_200_OK)

        if payload['type'] == 'interactive_message':
            self.incidence_ts['message_ts'] = payload['message_ts']
            if payload['callback_id'] == 'choice_made':
                if payload['actions'][0]['value'] == 'yes':
                    self.slack_client.api_call(
                        'dialog.open',
                        trigger_id=payload['trigger_id'],
                        dialog={
                            "title": "Andela Resources Tracker",
                            "submit_label": "Submit",
                            "notify_on_cancel": True,
                            "callback_id": "{}_incidence_report_1".format(
                                payload['user']['id']),
                            "elements": [
                                {
                                    'label': 'Asset',
                                    'type': 'select',
                                    'name': 'asset',
                                    'options': [
                                        {
                                            'label': '{}, {}, {}'.format(
                                                asset.asset_code,
                                                asset.serial_number,
                                                asset.model_number),
                                            'value': asset.id
                                        } for asset in assets
                                    ]
                                },
                                {
                                    'label': 'Incident type',
                                    'type': 'select',
                                    'name': 'incident_type',
                                    'options': [
                                        {'label': 'Loss', 'value': 'Loss'},
                                        {'label': 'Damage', 'value': 'Damage'}
                                    ]
                                },
                                {
                                    'label': 'Incident location',
                                    'type': 'text',
                                    'name': 'incident_location',
                                    'hint': '30 second summary of the problem',
                                },
                                {
                                    'label': 'Incident description',
                                    'type': 'textarea',
                                    'name': 'incident_description',
                                    'hint': '30 second description of \
                                    the problem',
                                },
                                {
                                    'label': 'Police Abstract Obtained',
                                    'type': 'textarea',
                                    'name': 'police_abstract_obtained',
                                    'hint': 'Summary of Police Report',
                                },
                            ]
                        }
                    )
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_200_OK)

        if payload['type'] == 'dialog_submission':
            smile = ":simple_smile::simple_smile::simple_smile:"
            call = self.slack_client.api_call(
                "chat.postEphemeral",
                username='BoluBot',
                channel=payload['channel']['id'],
                user=payload['user']['id'],
                response_url=payload['response_url'],
                response_type='ephemeral',
                text="Incident report logged. Thank you!!! {}".format(smile)
            )
            return Response(status=status.HTTP_200_OK)
