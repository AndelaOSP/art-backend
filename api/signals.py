"""
A module containing signals used to listen to specific events in the models
isort:skip_file
"""
# Third-Party Imports
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

# App Imports
from api.requestMiddleware import RequestMiddleware
from core import constants
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
    if sender._meta.db_table != "core_history" and current_request:
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
        notification_body = "{} submitted a new incident report {}."
        notification_title = "New Incident Report"
        notification_targets = User.objects.filter(is_superuser=True)
        notification_origin = instance.submitted_by
        incident_url = "{}/{}".format(reverse("incidence-reports-list"), instance.id)

        # create notifications to te different admins
        for target in notification_targets:
            notification = Notifications(
                title=notification_title,
                body=notification_body.format(target.email, incident_url),
                level=constants.INFO_NOTIFICATION,
                origin=notification_origin,
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
    incident_url = "{}/{}".format(reverse("incidence-reports-list"), instance.id)
    notification_body = "The status of incident report {} that you filed has been updated to `{}`.".format(
        incident_url, instance.incident_report_state
    )
    notification_title = "Incident Report Status Update"
    incident_report = AssetIncidentReport.objects.get(
        id=instance.asset_incident_report.id
    )
    if incident_report.submitted_by is not None:
        notification_target = incident_report.submitted_by
        # create notification
        notification = Notifications(
            title=notification_title,
            body=notification_body,
            level=constants.INFO_NOTIFICATION,
            target=notification_target,
        )
        notification.save()
