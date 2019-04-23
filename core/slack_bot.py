# Standard Library
import json
import logging
import os

# Third-Party Imports
from django.contrib.auth import get_user_model
from slackclient import SlackClient

# App Imports
from core.constants import DAMAGE, LOSS

logger = logging.getLogger(__name__)


class SlackIntegration(object):
    """Slack Integration class"""

    def __init__(self):
        """set the slack token"""
        slack_token = os.getenv('SLACK_TOKEN')
        self.incidence_ts = {}
        if slack_token:
            self.slack_client = SlackClient(slack_token)

    def process_user_data(self, users, email):
        found = False
        user_id = None
        for member in users:
            profile = member.get('profile')
            if profile and profile.get('email') == email:
                user_id = member.get('id')
                found = True
        return user_id, found

    def get_user_slack_id(self, user):
        """Get the slack user ID using the user email"""
        saved_user_id = user.slack_id
        user_email = user.email
        user_id = None
        if saved_user_id:
            email = self.get_user_slack_email(saved_user_id)
            if email == user_email:
                logger.info(f"Existing Slack ID valid.")
                return saved_user_id
        next_cursor = None
        slack_limit = os.getenv('SLACK_LIMIT', '1000')

        # slack_calls: To safeguard against too many calls to slack
        # users should be less than < SLACK_LIMIT * SLACK_CALLS
        slack_calls = os.getenv('SLACK_CALLS')
        try:
            slack_calls = int(slack_calls)
        except Exception:
            slack_calls = 10
        user_id = None
        cycles = 1
        response = self.slack_client.api_call("users.list", limit=slack_limit)
        if not response.get('ok'):
            logger.error('Unable to connect to slack')
            return None
        users = response.get("members")
        user_id, found = self.process_user_data(users, user_email)

        while not found:
            metadata = response.get('response_metadata')
            next_cursor = metadata.get('next_cursor')
            if not next_cursor or cycles >= slack_calls:
                break
            cycles += 1
            response = self.slack_client.api_call(
                "users.list", limit=slack_limit, cursor=next_cursor
            )
            users = response.get("members")
            user_id, found = self.process_user_data(users, user_email)
        if user_id:
            user.slack_id = user_id
            user.save()
            logger.info(f"No of Slack requests: {cycles}")
            return user_id
        logger.error(f"User not found for {user_email} after {cycles} requests")
        return user_id

    def send_message(self, message, user=None, channel=None):
        """Sends message to slack user or channel"""
        resp = {'ok': False}
        if hasattr(self, 'slack_client'):
            if user:
                slack_id = self.get_user_slack_id(user)
            elif channel:
                slack_id = channel
            else:
                slack_id = os.getenv('OPS_CHANNEL') or '#art-test'
            if slack_id:
                resp = self.slack_client.api_call(
                    "chat.postMessage",
                    channel=slack_id,
                    text=message,
                    username='@art-bot',
                    as_user=True,
                    icon_emoji=':ninja:',
                )
        if resp:
            error = resp.get('error')
            if error:
                logger.error(f'Error sending message for {slack_id}: {error}')
        return resp

    def get_user_slack_email(self, user_id):
        """Get the slack user ID using the user email"""

        response = self.slack_client.api_call("users.info", user=user_id)
        user = response.get("user")
        if response.get('ok'):
            profile = user.get('profile')
            email = profile.get('email')
            if email:
                return email
        logger.error(f"User not found for id: {user_id}")
        return None

    def send_incidence_report(self, data):
        """Sends incidence report from slack using a slash command"""
        from core.models import Asset, AssetIncidentReport

        User = get_user_model()
        payload = data.get('payload', None)
        if payload:
            payload = json.loads(payload)
            channel_id = payload.get('channel').get('id')
            user_id = payload.get('user').get('id')
        else:
            channel_id = data.get('channel_id')
            user_id = data.get('user_id')
        user_email = self.get_user_slack_email(user_id)

        if not payload:
            assets = Asset.objects.filter(assigned_to__user__email=user_email)
            if assets.count() == 0:
                no_asset_resp = self.slack_client.api_call(
                    'chat.postEphemeral',
                    username='@art-bot',
                    channel=channel_id,
                    user=user_id,
                    response_url=data.get('response_url'),
                    response_type='ephemeral',
                    text='Sorry, No Asset is assigned to you!!!',
                )
                if not no_asset_resp.get('ok'):
                    error = no_asset_resp.get('error')
                    logger.error(f'Error sending message for {user_id}: {error}')
                    return False
                return True

            dialog_response = self.slack_client.api_call(
                'dialog.open',
                trigger_id=data.get('trigger_id'),
                dialog={
                    "title": "Andela Resources Tracker",
                    "submit_label": "Submit",
                    "notify_on_cancel": True,
                    "callback_id": "{}_incidence_report_1".format(user_id),
                    "elements": [
                        {
                            'label': 'Asset',
                            'type': 'select',
                            'name': 'asset',
                            'options': [
                                {'label': '{}'.format(str(asset)), 'value': asset.id}
                                for asset in assets
                            ],
                        },
                        {
                            'label': 'Incident type',
                            'type': 'select',
                            'name': 'incident_type',
                            'options': [
                                {'label': LOSS, 'value': LOSS},
                                {'label': DAMAGE, 'value': DAMAGE},
                            ],
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
                            'hint': '30 second description of the problem',
                        },
                        {
                            'label': 'Police Abstract Obtained',
                            'type': 'textarea',
                            'name': 'police_abstract_obtained',
                            'hint': 'Summary of Police Report',
                        },
                    ],
                },
            )
            if not dialog_response.get('ok'):
                error = dialog_response.get('error')
                logger.error(
                    f'Error sending message for {user_id} - (email {user_email}): {error}'
                )
                return False
            return True

        if payload.get('type') == 'dialog_cancellation':
            return True

        if payload.get('type') == 'dialog_submission':
            report = AssetIncidentReport()
            report.asset = Asset.objects.get(id=int(payload.get('submission')['asset']))
            report.incident_type = payload.get('submission')['incident_type']
            report.incident_location = payload.get('submission')['incident_location']
            report.incident_description = payload.get('submission')[
                'incident_description'
            ]
            report.police_abstract_obtained = payload.get('submission')[
                'police_abstract_obtained'
            ]
            report.submitted_by = User.objects.get(email=user_email)
            try:
                report.save()
            except Exception as e:
                logger.error(str(e))
                return False
            else:
                smile = ":simple_smile::simple_smile::simple_smile:"
                self.slack_client.api_call(
                    "chat.postEphemeral",
                    username='@art-bot',
                    channel=channel_id,
                    user=user_id,
                    response_url=payload.get('response_url'),
                    response_type='ephemeral',
                    text="Incident report logged. Thank you!!! {}".format(smile),
                )
            return True
