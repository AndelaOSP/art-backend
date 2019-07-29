# Third-Party Imports
from django.db import models

# App Imports
from core import constants


class History(models.Model):
    table_name = models.CharField(max_length=255, blank=False, editable=False)
    user = models.ForeignKey("User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    item_id = models.CharField(max_length=255, null=False, blank=False, editable=False)
    action = models.CharField(
        max_length=7, null=False, blank=False, choices=constants.ACTIONS, editable=False
    )
    body = models.TextField(default="", editable=False)

    class Meta:
        verbose_name_plural = "History model"

    def __str__(self):
        return self.action
