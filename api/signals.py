"""
A module containing signals used to listen to specific events in the models
isort:skip_file
"""
# Third-Party Imports
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

# App Imports
from api.requestMiddleware import RequestMiddleware
from core import constants
from core.constants import TABLES
from core.models import (  # isort:skip
    AssetIncidentReport,
    History,
    Notifications,
    StateTransition,
    User,
)


@receiver(post_save)
@receiver(post_delete)
def track_application_actions(sender, instance, **kwargs):
    current_request = RequestMiddleware.get_request()
    if (
        sender._meta.db_table not in TABLES
        and hasattr(current_request, "user")
        and hasattr(instance, "id")
    ):
        data = instance.__dict__.copy()
        data.__delitem__("_state")
        try:
            history = History(
                table_name=str(instance._meta.db_table),
                user=current_request.user,
                item_id=instance.id,
                action=current_request.method,
                body=data,
            )
            history.save()
        except ValueError:
            pass


@receiver(post_save, sender=AssetIncidentReport)
def create_notification_on_incident_report_submission(**kwargs):
    """
    Create a notification to admin users when a user creates an incident report
    :param kwargs:
    :return:
    """
    instance = kwargs["instance"]
    # if a new notification has been  created
    if kwargs.get("created", False) is True:
        notification_targets = User.objects.filter(is_superuser=True)
        incident_url = f'{reverse("incidence-reports-list")}/{instance.id}'

        # create notifications to te different admins
        # carry out as a transaction to eliminate the computational cost of individual operations
        # and  also to  benefit from having transaction roll-backs if any of the items fail.
        with transaction.atomic():
            for target in notification_targets:
                notification = Notifications(
                    title=constants.INCIDENT_REPORT_CREATED_NOTIFICATION_TITLE,
                    body=constants.INCIDENT_REPORT_CREATED_NOTIFICATION_BODY.substitute(
                        email=target.email, link=incident_url
                    ),
                    level=constants.INFO_NOTIFICATION,
                    origin=instance.submitted_by,
                    target=target,
                )
                notification.save()
                # send email to user


@receiver(post_save, sender=StateTransition)
def alert_user_when_incident_report_status_is_updated(**kwargs):
    """
    When the status of the incident report is modified, alert the user that filed the report
    :param kwargs:
    :return:
    """
    instance = kwargs["instance"]
    # notification details
    incident_url = f'{reverse("incidence-reports-list")}/{instance.id}'
    incident_report = AssetIncidentReport.objects.get(
        id=instance.asset_incident_report.id
    )
    if incident_report.submitted_by is not None:
        # create notification
        notification = Notifications(
            title=constants.INCIDENT_REPORT_STATUS_UPDATED_NOTIFICATION_TITLE,
            body=constants.INCIDENT_REPORT_STATUS_UPDATED_BODY.substitute(
                link=incident_url, current_status=instance.incident_report_state
            ),
            level=constants.INFO_NOTIFICATION,
            target=incident_report.submitted_by,
        )
        notification.save()
