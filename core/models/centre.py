# Standard Library
import logging

# Third-Party Imports
from django.core.exceptions import ValidationError
from django.db import models
from pycountry import countries

# App Imports
from core.managers import CaseInsensitiveManager

logger = logging.getLogger(__name__)


class AndelaCentre(models.Model):
    name = models.CharField(max_length=25, unique=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CaseInsensitiveManager()

    class Meta:
        verbose_name_plural = 'Andela Centres'

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        try:
            country = countries.lookup(self.name)
        except Exception:
            raise ValidationError('{} is not a valid country'.format(self.name))
        else:
            self.name = country.name

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(str(e))
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


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
        except Exception as e:
            raise ValidationError(str(e))
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


class OfficeBlock(models.Model):
    name = models.CharField(max_length=50)
    location = models.ForeignKey('AndelaCentre', on_delete=models.PROTECT, null=True)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(str(e))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Office Block"
        unique_together = (('name', 'location'),)

    def __str__(self):
        return self.name


class OfficeFloor(models.Model):
    number = models.PositiveIntegerField()
    block = models.ForeignKey(OfficeBlock, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('block', 'number'),)
        verbose_name = 'Office Floor'
        ordering = ['-id']

    def __str__(self):
        return "{}".format(self.number)


class OfficeFloorSection(models.Model):
    name = models.CharField(max_length=100)
    floor = models.ForeignKey(OfficeFloor, on_delete=models.PROTECT)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        """
        Validate office floor section name
        """
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('floor', 'name'),)
        verbose_name = 'Office Floor Section'
        ordering = ['-id']

    def __str__(self):
        return self.name


class OfficeWorkspace(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(OfficeFloorSection, on_delete=models.PROTECT)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        """
        Validate office workspace name
        """
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(e)
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            self._create_assignee_object_for_workspace()

    def _create_assignee_object_for_workspace(self):
        from .asset import AssetAssignee

        AssetAssignee.objects.get_or_create(workspace=self)

    class Meta:
        verbose_name = 'Office Workspace'
        unique_together = (("name", "section"),)

    def __str__(self):
        return self.name
