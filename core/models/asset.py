from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import ForeignKey, PositiveIntegerField
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime

from .user import SecurityUser
from core.slack_bot import SlackIntegration
from core.validator import validate_date

AVAILABLE = "Available"
ALLOCATED = "Allocated"
LOST = "Lost"
DAMAGED = "Damaged"

ASSET_STATUSES = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (LOST, "Lost"),
    (DAMAGED, "Damaged"),
)

CHECKIN = "Checkin"
CHECKOUT = "Checkout"

LOG_TYPE_CHOICES = ((CHECKIN, "Checkin"), (CHECKOUT, "Checkout"))

LOSS = "Loss"
DAMAGE = "Damage"

INCIDENT_TYPES = ((LOSS, "Loss"), (DAMAGE, "Damage"))

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

SCREEN_SIZES = ((13, '13"'), (15, '15"'), (17, '17"'))

MEMORY = ((4, "4GB"), (8, "8GB"), (16, "16GB"), (32, "32GB"))

STORAGE_SIZES = ((128, "128GB"), (256, "256GB"), (512, "512GB"))

YEAR_CHOICES = []
for year in range(2013, (datetime.now().year + 1)):
    YEAR_CHOICES.append((year, year))

slack = SlackIntegration()


class AssetCategory(models.Model):
    """ Stores all asset categories """

    category_name = models.CharField(unique=True, max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        if not self.category_name:
            raise ValidationError("Category is required")

        self.category_name = self.category_name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Asset Categories"
        ordering = ["-id"]

    def __str__(self):
        return self.category_name


class AssetSubCategory(models.Model):
    """Stores all asset sub categories"""

    sub_category_name = models.CharField(
        unique=True,
        max_length=40,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)
    asset_category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)

    def clean(self):
        if not self.asset_category:
            raise ValidationError("Category is required")

        self.sub_category_name = self.sub_category_name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Asset SubCategories"
        ordering = ["-id"]

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

    def clean(self):
        if not self.asset_sub_category:
            raise ValidationError("Sub category is required")

        self.asset_type = self.asset_type.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Type"
        ordering = ["-id"]

    def __str__(self):
        return self.asset_type


class AssetMake(models.Model):
    """ stores all asset makes """

    make_label = models.CharField(
        unique=True, max_length=40, null=False, verbose_name="Asset Make"
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    def clean(self):
        if not self.asset_type:
            raise ValidationError("Type is required")

        self.make_label = self.make_label.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Make"
        ordering = ["-id"]

    def __str__(self):
        return self.make_label


class AssetModelNumber(models.Model):
    model_number = models.CharField(unique=True, max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    make_label = models.ForeignKey(
        AssetMake,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Asset Make"
    )

    def clean(self):
        self.model_number = self.model_number.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Model Number"
        ordering = ["-id"]

    def __str__(self):
        return self.model_number


class AssetSpecs(models.Model):
    year_of_manufacture = models.IntegerField(
        null=True, blank=True, choices=YEAR_CHOICES
    )
    processor_type = models.CharField(
        max_length=300, blank=True, null=True, choices=PROCESSOR_TYPE
    )
    processor_speed = models.FloatField(
        null=True,
        blank=True,
        choices=PROCESSOR_SPEED
    )
    screen_size = models.IntegerField(
        null=True,
        blank=True,
        choices=SCREEN_SIZES
    )
    storage = models.IntegerField(null=True, blank=True, choices=STORAGE_SIZES)
    memory = models.IntegerField(null=True, blank=True, choices=MEMORY)

    class Meta:
        verbose_name = "Asset Specification"
        unique_together = (
            "storage",
            "memory",
            "screen_size",
            "processor_speed",
            "year_of_manufacture",
            "processor_type",
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.memory}GB RAM, " \
            f"{self.storage}GB, " \
            f"{self.processor_speed}GHz," \
            f'{self.screen_size}"'


class Asset(models.Model):
    """Stores all assets"""

    asset_code = models.CharField(
        unique=True,
        null=True,
        blank=True,
        max_length=50
    )
    serial_number = models.CharField(
        unique=True,
        null=True,
        blank=True,
        max_length=50
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    purchase_date = models.DateField(
        validators=[validate_date],
        null=True,
        blank=True
    )
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    # allocations = GenericRelation(AllocationHistory)
    model_number = models.ForeignKey(
        AssetModelNumber, null=True, on_delete=models.PROTECT
    )
    specs = models.ForeignKey(
        AssetSpecs, blank=True, null=True, on_delete=models.PROTECT
    )
    verified = models.BooleanField(default=True)

    def clean(self):
        if not self.asset_code and not self.serial_number:
            raise ValidationError(
                ("Please provide either the serial number, " \
                "asset code or both."),
                code="required",
            )

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
        super(Asset, self).save(*args, **kwargs)

    def __str__(self):
        return "{}, {}, {}".format(
            self.asset_code, self.serial_number, self.model_number
        )

    class Meta:
        ordering = ["-id"]


class AllocationHistory(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    current_allocation_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='current'
    )
    current_allocation_object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    current_allocation = GenericForeignKey(
        'current_allocation_content_type',
        'current_allocation_object_id'
    )
    previous_allocation_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='previous'
    )
    previous_allocation_object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    previous_allocation = GenericForeignKey(
        'previous_allocation_content_type',
        'previous_allocation_object_id'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Allocation History"
        ordering = ["-id"]

    def clean(self):
        # import ipdb; ipdb.set_trace()
        last_saved_asset_status = self.asset.assetstatus_set.first()
        if last_saved_asset_status.current_status != AVAILABLE:
            raise ValidationError("You can only allocate available assets")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AllocationHistory, self).save(*args, **kwargs)

    def __str__(self):
        if self.current_allocation:
            return f'{self.asset} allocated to {self.current_allocation}'
        else:
            return f'{self.asset} last allocated to {self.previous_allocation}'


class AssetLog(models.Model):
    """Stores checkin/Checkout asset logs"""

    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    checked_by = models.ForeignKey(
        SecurityUser,
        blank=True,
        on_delete=models.PROTECT
    )
    log_type = models.CharField(
        max_length=10,
        blank=False,
        choices=LOG_TYPE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        if not self.log_type:
            raise ValidationError("Log type is required.", code="required")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Log"
        ordering = ["-id"]


class AssetStatus(models.Model):
    """Stores the previous and current status of models"""

    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    current_status = models.CharField(
        max_length=50,
        choices=ASSET_STATUSES,
        default=ASSET_STATUSES[0][0]
    )
    previous_status = models.CharField(
        max_length=50,
        choices=ASSET_STATUSES,
        null=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Asset Statuses"
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        try:
            latest_record = AssetStatus.objects.filter(asset=self.asset).latest(
                "created_at"
            )
            self.previous_status = latest_record.current_status
        except Exception:
            self.previous_status = None
        self.full_clean()
        super(AssetStatus, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.asset.asset_code} - {self.current_status}'



class AssetCondition(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)

    notes = models.TextField(editable=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Asset Condition"
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        super(AssetCondition, self).save(*args, **kwargs)


class AssetIncidentReport(models.Model):
    asset = models.ForeignKey(Asset, null=False, on_delete=models.PROTECT)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    incident_location = models.CharField(max_length=50, null=False, blank=False)
    incident_description = models.TextField(null=False, blank=False)
    injuries_sustained = models.TextField(null=True, blank=True)
    loss_of_property = models.TextField(null=True, blank=True)
    witnesses = models.TextField(null=True, blank=True)
    police_abstract_obtained = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    submitted_by = models.ForeignKey(
        "User", blank=False, null=True, on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.incident_type}: {self.asset}"

    class Meta:
        ordering = ["-id"]


@receiver(post_save, sender=Asset)
def create_initial_asset_status(sender, **kwargs):
    asset = kwargs.get('instance')

    if kwargs.get('created'):
        AssetStatus.objects.create(asset=asset)

# @receiver(post_save, sender=AssetCondition)
# def save_notes(sender, **kwargs):
#     new_condition = kwargs.get("instance")
#     related_asset = new_condition.asset
#     if not new_condition.notes == related_asset.notes:
#         related_asset.notes = new_condition.notes
#         related_asset.save()


@receiver(post_save, sender=AllocationHistory)
def update_asset_status_when_allocation_changes(sender, **kwargs):
    allocation_history = kwargs.get('instance')

    if kwargs.get('created'):
        last_status = AssetStatus.objects.filter(
            asset=allocation_history.asset
        ).latest('created_at')
        if allocation_history.current_allocation:
            new_status = AssetStatus.objects.create(
                asset=allocation_history.asset,
                current_status=ALLOCATED,
                previous_status=last_status.current_status
            )
    # import ipdb; ipdb.set_trace()

@receiver(post_save, sender=AssetStatus)
def update_asset_allocation_history_when_status_changes(sender, **kwargs):
    asset_status = kwargs.get('instance')

    if kwargs.get('created'):
        try:
            last_allocation_record = AllocationHistory.objects.filter(
                asset=asset_status.asset,
            ).latest('created_at')
            if asset_status.current_status == AVAILABLE:
                AllocationHistory.objects.create(
                    asset=asset_status.asset,
                    previous_allocation=last_allocation_record.current_allocation
                )
        except Exception as e:
            pass
