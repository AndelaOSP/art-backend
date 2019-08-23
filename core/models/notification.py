# Standard Library
import datetime

# Third-Party Imports
from django.db import models
from django.utils.timesince import timesince

# App Imports
from core import constants


class Notifications(models.Model):
    """
    A model representing a notification object
    Nomenclature based on https://www.w3.org/TR/notifications/
    Generalized Format for notifications body::
        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::
        <user> <reached level 60> <1 minute ago>
        <user2> <commented on> <url/post/1d> <2 hours ago>
        <user> <started follow> <user2> <8 minutes ago>
        <user> <closed> <issue 70> on <topic> <about 2 hours ago>
    """

    title = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        help_text="A string label for the notification",
    )
    body = models.TextField(help_text="further details about a notification")
    level = models.CharField(
        max_length=50,
        choices=constants.NOTIFICATION_LEVELS,
        default=constants.INFO_NOTIFICATION,
        help_text="severity level of a notification",
    )
    origin = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="the notification's sender",
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    target = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="the notification's recipient",
        related_name="received_notifications",
    )
    icon_url = models.URLField(blank=False, null=False)
    created_at = models.DateField(auto_now_add=True)
    read = models.BooleanField(
        default=False,
        help_text="boolean indicating if notification has been read or not",
    )
    read_at = models.DateField(blank=True, null=True)
    emailed = models.BooleanField(
        default=False,
        help_text="boolean indicating if notification has been emailed or not",
    )
    emailed_at = models.DateField(blank=True, null=True)

    def timesince(self, now=datetime.datetime.now()):
        """
        get the time since the notification was created to the time specified
        """
        return timesince(self.created_at, now)

    def mark_as_read(self):
        """mark notification as viewed by used"""
        if self.read is False:
            self.read = True
            self.save()

    def mark_as_unread(self):
        """mark viewed notification as not viewed """
        if self.read:
            self.read = False
            self.save()
