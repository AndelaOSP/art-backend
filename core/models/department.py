import logging

from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers


logger = logging.getLogger(__name__)


class Department(models.Model):
    """ Stores all departments """

    name = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except ValidationError as error:
            raise serializers.ValidationError(error)
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            self._create_assignee_object_for_department()

    def _create_assignee_object_for_department(self):
        from .asset import AssetAssignee
        AssetAssignee.objects.get_or_create(department=self)

    class Meta:
        verbose_name = "Department"

    def __str__(self):
        return self.name
