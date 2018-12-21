import logging
import os
import uuid

from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError

from .user import SecurityUser
from core.slack_bot import SlackIntegration
from core.validator import validate_date
from core.managers import CaseInsensitiveManager

AVAILABLE = "Available"
ALLOCATED = "Allocated"
LOST = "Lost"
DAMAGED = "Damaged"

ASSET_STATUSES = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (LOST, "Lost"),
    (DAMAGED, "Damaged")
)
KENYA = "Kenya"
NIGERIA = "Nigeria"
RWANDA = "Rwanda"
UGANDA = "Uganda"
EGYPT = "Egypt"
USA = "USA"
GHANA = "Ghana"

COUNTRIES = (
    (EGYPT, "Egypt"),
    (GHANA, "Ghana"),
    (KENYA, "Kenya"),
    (NIGERIA, "Nigeria"),
    (RWANDA, "Rwanda"),
    (UGANDA, "Uganda"),
    (USA, "USA"),
)

CHECKIN = "Checkin"
CHECKOUT = "Checkout"

LOG_TYPE_CHOICES = (
    (CHECKIN, "Checkin"),
    (CHECKOUT, "Checkout"),
)

LOSS = 'Loss'
DAMAGE = 'Damage'

INCIDENT_TYPES = (
    (LOSS, 'Loss'),
    (DAMAGE, 'Damage')
)

PROCESSOR_TYPE = (
    ("Intel core i3", "Intel core i3"),
    ("Intel core i5", "Intel core i5"),
    ("Intel core i7", "Intel core i7"),
)

PROCESSOR_SPEED = (
    (1.8, "1.8GHz"),
    (2.3, "2.3GHz"),
    (3.0, "3.0GHz"),
    (3.4, "3.4GHz")
)

SCREEN_SIZES = (
    (13, "13\""),
    (15, "15\""),
    (17, "17\"")
)

MEMORY = (
    (4, "4GB"),
    (8, "8GB"),
    (16, "16GB"),
    (32, "32GB")
)

STORAGE_SIZES = (
    (128, "128GB"),
    (256, "256GB"),
    (512, "512GB")
)
YEAR_CHOICES = []
for year in range(2013, (datetime.now().year + 1)):
    YEAR_CHOICES.append((year, year))

slack = SlackIntegration()

logger = logging.getLogger(__name__)


class AssetCategory(models.Model):
    """ Stores all asset categories """
    category_name = models.CharField(unique=True, max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.category_name:
            raise ValidationError('Category is required')

        self.category_name = self.category_name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Asset Categories'
        ordering = ['-id']

    def __str__(self):
        return self.category_name


class AssetSubCategory(models.Model):
    """Stores all asset sub categories"""
    sub_category_name = models.CharField(unique=True, max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)
    asset_category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_category:
            raise ValidationError('Category is required')

        self.sub_category_name = self.sub_category_name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Asset SubCategories'
        ordering = ['-id']

    def __str__(self):
        return self.sub_category_name


class AssetType(models.Model):
    """Stores all asset types"""
    asset_type = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    asset_sub_category = models.ForeignKey(
        AssetSubCategory,
        on_delete=models.PROTECT
    )
    has_specs = models.BooleanField(blank=False, default=False)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_sub_category:
            raise ValidationError('Sub category is required')

        self.asset_type = self.asset_type.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Type"
        ordering = ['-id']

    def __str__(self):
        return self.asset_type


class AssetMake(models.Model):
    """ stores all asset makes """
    make_label = models.CharField(unique=True, max_length=40, null=False, verbose_name="Asset Make")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_type:
            raise ValidationError('Type is required')

        self.make_label = self.make_label.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Make"
        ordering = ['-id']

    def __str__(self):
        return self.make_label


class AssetModelNumber(models.Model):
    model_number = models.CharField(unique=True, max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    make_label = models.ForeignKey(AssetMake, null=True, on_delete=models.PROTECT, verbose_name="Asset Make")
    objects = CaseInsensitiveManager()

    def clean(self):
        self.model_number = self.model_number.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Model Number"
        ordering = ['-id']

    def __str__(self):
        return self.model_number


class AssetSpecs(models.Model):
    year_of_manufacture = models.IntegerField(null=True, blank=True, choices=YEAR_CHOICES)
    processor_type = models.CharField(max_length=300, blank=True, null=True, choices=PROCESSOR_TYPE)
    processor_speed = models.FloatField(null=True, blank=True, choices=PROCESSOR_SPEED)
    screen_size = models.IntegerField(null=True, blank=True, choices=SCREEN_SIZES)
    storage = models.IntegerField(null=True, blank=True, choices=STORAGE_SIZES)
    memory = models.IntegerField(null=True, blank=True, choices=MEMORY)

    class Meta:
        verbose_name = "Asset Specification"
        unique_together = (
            "storage", "memory", "screen_size", "processor_speed",
            "year_of_manufacture", "processor_type"
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.memory}GB RAM, {self.storage}GB, {self.processor_speed}GHz, {self.screen_size}\""


class Asset(models.Model):
    """Stores all assets"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    asset_code = models.CharField(unique=True, null=True, blank=True, max_length=50)
    serial_number = models.CharField(unique=True, null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    asset_location = models.ForeignKey('AndelaCentre', blank=True, null=True, on_delete=models.PROTECT)
    purchase_date = models.DateField(validators=[validate_date], null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('AssetAssignee', blank=True, editable=False, null=True, on_delete=models.PROTECT)
    model_number = models.ForeignKey(AssetModelNumber, null=True, on_delete=models.PROTECT)
    current_status = models.CharField(editable=False, max_length=50)
    notes = models.TextField(editable=False, default=" ")
    specs = models.ForeignKey(AssetSpecs, blank=True, null=True, on_delete=models.PROTECT)
    verified = models.BooleanField(default=True)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_code and not self.serial_number:
            raise ValidationError((
                'Please provide either the serial number, asset code or both.'
            ), code='required')

        if self.serial_number is None:
            self.asset_code = self.asset_code.upper()

        elif self.asset_code is None:
            self.serial_number = self.serial_number.upper()

        else:
            self.asset_code = self.asset_code.upper()
            self.serial_number = self.serial_number.upper()

    def save(self, *args, **kwargs):
        """
        Validate either asset code, serial number
        are provided and an existing status is given
        """
        self.full_clean()
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            self._save_initial_asset_status()

    def _save_initial_asset_status(self):
        existing_status = AssetStatus.objects.filter(asset=self)
        if not existing_status:
            AssetStatus.objects.create(asset=self, current_status=AVAILABLE)
            self.current_status = AVAILABLE
            self.save()

    def __str__(self):
        return '{}, {}, {}'.format(self.asset_code, self.serial_number, self.model_number)

    class Meta:
        ordering = ['-id']
        unique_together = ("asset_code", "serial_number",)


class AssetAssignee(models.Model):
    department = models.OneToOneField('Department', null=True, blank=True, on_delete=models.CASCADE)
    workspace = models.OneToOneField('OfficeWorkspace', null=True, blank=True, on_delete=models.CASCADE)
    user = models.OneToOneField('User', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        assignee = self.workspace or self.department or self.user
        if assignee:
            return str(assignee)
        else:
            raise ValidationError(
                message="No Department, Workspace or User for this AssetAssignee")

    class Meta:
        ordering = ['-id']

    @property
    def first_name(self):
        if self.department:
            return self.department.name
        if self.workspace:
            return self.workspace.name
        if self.user:
            return self.user.first_name

    @property
    def last_name(self):
        if self.department:
            return self.department.name
        if self.workspace:
            return self.workspace.section
        if self.user:
            return self.user.last_name

    @property
    def email(self):
        if self.department:
            return self.department.name
        if self.workspace:
            return self.workspace.name
        if self.user:
            return self.user.email


class AssetLog(models.Model):
    """Stores checkin/Checkout asset logs"""
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    checked_by = models.ForeignKey(SecurityUser, blank=True, on_delete=models.PROTECT)
    log_type = models.CharField(max_length=10, blank=False, choices=LOG_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        if not self.log_type:
            raise ValidationError('Log type is required.', code='required')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Log"
        ordering = ['-id']


class AssetStatus(models.Model):
    """Stores the previous and current status of models"""
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    current_status = models.CharField(max_length=50, choices=ASSET_STATUSES, default=ASSET_STATUSES[0][0])
    previous_status = models.CharField(max_length=50, choices=ASSET_STATUSES, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Statuses'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        try:
            latest_record = AssetStatus.objects.filter(asset=self.asset).latest('created_at')
            self.previous_status = latest_record.current_status
        except Exception:
            self.previous_status = None
        self.full_clean()
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            self._set_current_status_for_asset()
            self._check_asset_limit()
            self._new_allocation_history_when_asset_is_made_available()

    def _set_current_status_for_asset(self):
        current_asset = self.asset
        current_asset.current_status = self.current_status
        if self.current_status == AVAILABLE:
            current_asset.assigned_to = None
        current_asset.save()

    def _check_asset_limit(self):
        """Check the assets have not exceeded the limit"""
        model_number = self.asset.model_number
        available_assets = Asset.objects.filter(current_status='Available', model_number=model_number).count()
        if available_assets <= int(os.environ.get('ASSET_LIMIT', 0)):
            message = "Warning!! The number of available {} ".format(
                model_number) + " is {}".format(available_assets)
            slack.send_message(message)

    def _new_allocation_history_when_asset_is_made_available(self):
        try:
            last_allocation_record = AllocationHistory.objects.filter(asset=self.asset).latest('created_at')
        except Exception as e:
            logger.warning(str(e))
        else:
            if self.current_status == AVAILABLE and last_allocation_record:
                AllocationHistory.objects.create(
                    asset=self.asset,
                    previous_owner=last_allocation_record.current_owner,
                    current_owner=None,
                )


class AllocationHistory(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    current_owner = models.ForeignKey(
        'AssetAssignee', related_name='current_owner_asset',
        blank=True, null=True, on_delete=models.PROTECT
    )
    previous_owner = models.ForeignKey(
        'AssetAssignee', related_name='previous_owner_asset',
        editable=False, blank=True, null=True, on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Allocation History"
        ordering = ['-id']

    def clean(self):
        if self.asset.current_status != AVAILABLE:
            raise ValidationError("You can only allocate available assets")

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            latest_record = AllocationHistory.objects.filter(asset=self.asset).latest('created_at')
            self.previous_owner = latest_record.current_owner
        except Exception:
            self.previous_owner = None
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            asset = self.asset
            asset.assigned_to = self.current_owner
            asset.save()
            self._create_asset_status_when_asset_is_allocated()

    def _create_asset_status_when_asset_is_allocated(self):
        last_status = AssetStatus.objects.filter(asset=self.asset).latest('created_at')
        if self.current_owner:
            AssetStatus.objects.create(
                asset=self.asset, current_status=ALLOCATED,
                previous_status=last_status.current_status,
            )

    def _send_notification(self):
        asset = self.asset
        user = None

        if asset.assigned_to and asset.current_status == ALLOCATED:
            message = "The asset with serial number {} and asset code {} ".format(
                asset.serial_number, asset.asset_code) + "has been allocated to you."
            user = self.current_owner
        elif (not asset.assigned_to and self.previous_owner):
            message = "The asset with serial number {} and asset code {} ".format(
                asset.serial_number, asset.asset_code) + "has been de-allocated from you."
            user = self.previous_owner

        if user and hasattr(user, 'email'):
            slack.send_message(message, user=user)


class AssetCondition(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    notes = models.TextField(editable=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Condition'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
        else:
            self._save_notes()

    def _save_notes(self):
        related_asset = self.asset
        if self.notes != related_asset.notes:
            related_asset.notes = self.notes
            related_asset.save()


class AssetIncidentReport(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    incident_location = models.CharField(max_length=50, null=False, blank=False)
    incident_description = models.TextField(null=False, blank=False)
    injuries_sustained = models.TextField(null=True, blank=True)
    loss_of_property = models.TextField(null=True, blank=True)
    witnesses = models.TextField(null=True, blank=True)
    police_abstract_obtained = models.CharField(max_length=255, blank=False, null=False)
    submitted_by = models.ForeignKey('User', blank=False, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.incident_type}: {self.asset}"

    class Meta:
        ordering = ['-id']


class AndelaCentre(models.Model):
    centre_name = models.CharField(max_length=25, unique=True, null=False, blank=False)
    country = models.CharField(max_length=25, null=False, blank=False, choices=COUNTRIES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CaseInsensitiveManager()

    class Meta:
        verbose_name_plural = 'Andela Centres'

    def __str__(self):
        return self.centre_name
