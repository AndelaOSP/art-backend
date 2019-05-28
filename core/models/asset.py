# Standard Library
import logging
import os
import uuid

# Third-Party Imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# App Imports
from core import constants
from core.managers import CaseInsensitiveManager
from core.slack_bot import SlackIntegration
from core.validator import validate_date

slack = SlackIntegration()

logger = logging.getLogger(__name__)


class AssetCategory(models.Model):
    """ Stores all asset categories """

    name = models.CharField(unique=True, max_length=40)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.name:
            raise ValidationError("Category is required")

        self.name = self.name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Asset Categories"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class AssetSubCategory(models.Model):
    """Stores all asset sub categories"""

    name = models.CharField(unique=True, max_length=40)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)
    asset_category = models.ForeignKey("AssetCategory", on_delete=models.PROTECT)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_category:
            raise ValidationError("Category is required")

        self.name = self.name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Asset SubCategories"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class AssetType(models.Model):
    """Stores all asset types"""

    name = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    asset_sub_category = models.ForeignKey("AssetSubCategory", on_delete=models.PROTECT)
    has_specs = models.BooleanField(default=False)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_sub_category:
            raise ValidationError("Sub category is required")

        self.name = self.name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Type"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class AssetMake(models.Model):
    """ stores all asset makes """

    name = models.CharField(unique=True, max_length=40, verbose_name="Asset Make")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)
    asset_type = models.ForeignKey("AssetType", on_delete=models.PROTECT)

    objects = CaseInsensitiveManager()

    def clean(self):
        if not self.asset_type:
            raise ValidationError("Type is required")

        self.name = self.name.title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Make"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class AssetModelNumber(models.Model):
    name = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    asset_make = models.ForeignKey(
        "AssetMake", null=True, on_delete=models.PROTECT, verbose_name="Asset Make"
    )
    objects = CaseInsensitiveManager()

    def clean(self):
        self.name = self.name.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Model Number"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class AssetSpecs(models.Model):
    year_of_manufacture = models.IntegerField(
        null=True, blank=True, choices=constants.YEAR_CHOICES
    )
    processor_type = models.CharField(
        max_length=300, blank=True, null=True, choices=constants.PROCESSOR_TYPE
    )
    processor_speed = models.FloatField(
        null=True, blank=True, choices=constants.PROCESSOR_SPEED
    )
    screen_size = models.IntegerField(
        null=True, blank=True, choices=constants.SCREEN_SIZES
    )
    storage = models.IntegerField(
        null=True, blank=True, choices=constants.STORAGE_SIZES
    )
    memory = models.IntegerField(null=True, blank=True, choices=constants.MEMORY)

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
        return f"{self.memory}GB RAM, {self.storage}GB, {self.processor_speed}GHz, {self.screen_size}"


class Asset(models.Model):
    """Stores all assets"""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    asset_code = models.CharField(unique=True, null=True, blank=True, max_length=50)
    serial_number = models.CharField(unique=True, null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    asset_location = models.ForeignKey(
        "AndelaCentre", blank=True, null=True, on_delete=models.PROTECT
    )
    purchase_date = models.DateField(validators=[validate_date], null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey(
        "AssetAssignee", blank=True, editable=False, null=True, on_delete=models.PROTECT
    )
    owned_by = models.ForeignKey(
        "AssetOwner",
        blank=True,
        editable=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="owned_by",
    )
    model_number = models.ForeignKey(
        "AssetModelNumber", null=True, on_delete=models.PROTECT
    )
    current_status = models.CharField(editable=False, max_length=50)
    notes = models.TextField(editable=False, default=" ")
    specs = models.ForeignKey(
        "AssetSpecs", blank=True, null=True, on_delete=models.PROTECT
    )
    verified = models.BooleanField(default=True)
    invoice_receipt = models.FileField(
        null=True, blank=True, upload_to="invoice_receipts/"
    )
    department = models.ForeignKey(
        "Department", null=True, blank=True, on_delete=models.PROTECT
    )
    active = models.BooleanField(blank=True, null=True)
    paid_or_postpaid = models.CharField(
        blank=True, null=True, max_length=8, choices=constants.SIMCARD_ASSET_OPTIONS
    )
    objects = CaseInsensitiveManager()

    def __str__(self):
        return "{}, {}, {}".format(
            self.asset_code, self.serial_number, self.model_number
        )

    class Meta:
        ordering = ["-id"]
        unique_together = ("asset_code", "serial_number")
        indexes = [models.Index(fields=["current_status", "verified"])]

    def clean(self):
        if not self.asset_code and not self.serial_number:
            raise ValidationError(
                ("Please provide either the serial number, asset code or both."),
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
        try:
            super().save(*args, **kwargs)
        except Exception:
            raise
        else:
            self._save_initial_asset_status()

    def _save_initial_asset_status(self):
        existing_status = AssetStatus.objects.filter(asset=self)
        if not existing_status:
            AssetStatus.objects.create(asset=self, current_status=constants.AVAILABLE)
            self.current_status = constants.AVAILABLE
            self.save()

    def _get_asset_category(self):
        return self._get_asset_sub_category().asset_category

    def _get_asset_sub_category(self):
        return self._get_asset_type().asset_sub_category

    def _get_asset_make(self):
        return self.model_number.asset_make

    def _get_asset_type(self):
        return self._get_asset_make().asset_type

    @property
    def asset_category(self):
        return self._get_asset_category().name

    @property
    def asset_sub_category(self):
        return self._get_asset_sub_category().name

    @property
    def asset_make(self):
        return self._get_asset_make().name

    @property
    def asset_type(self):
        return self._get_asset_type().name


class AssetAssigneeOrOwner(models.Model):
    department = models.OneToOneField(
        "Department", null=True, blank=True, on_delete=models.CASCADE
    )
    workspace = models.OneToOneField(
        "OfficeWorkspace", null=True, blank=True, on_delete=models.CASCADE
    )
    user = models.OneToOneField("User", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        assignee = self.workspace or self.department or self.user
        if assignee:
            return str(assignee)
        else:
            raise ValidationError(
                message="No Department, Workspace or User for this AssetAssignee/Owner"
            )

    class Meta:
        ordering = ["-id"]
        abstract = True

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


class AssetAssignee(AssetAssigneeOrOwner):
    pass


class AssetOwner(AssetAssigneeOrOwner):
    pass


class AssetLog(models.Model):
    """Stores checkin/Checkout asset logs"""

    asset = models.ForeignKey("Asset", on_delete=models.PROTECT)
    checked_by = models.ForeignKey("User", blank=True, on_delete=models.PROTECT)
    log_type = models.CharField(max_length=10, choices=constants.ASSET_LOG_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        if not self.log_type:
            raise ValidationError("Log type is required.", code="required")

    def save(self, *args, **kwargs):
        self.full_clean()
        log = AssetLog.objects.filter(asset=self.asset).first()
        if log and log.log_type == self.log_type:
            return None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Log"
        ordering = ["-id"]


class AssetStatus(models.Model):
    """Stores the previous and current status of models"""

    asset = models.ForeignKey("Asset", on_delete=models.PROTECT)
    current_status = models.CharField(
        max_length=50, choices=constants.ASSET_STATUSES, default=constants.AVAILABLE
    )
    previous_status = models.CharField(
        max_length=50,
        choices=constants.ASSET_STATUSES,
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
        try:
            super().save(*args, **kwargs)
        except Exception:
            raise
        else:
            self._set_current_status_for_asset()
            self._check_asset_limit()
            self._new_allocation_history_when_asset_is_made_available()

    def _set_current_status_for_asset(self):
        current_asset = self.asset
        current_asset.current_status = self.current_status
        if self.current_status == constants.AVAILABLE:
            current_asset.assigned_to = None
        current_asset.save()

    def _check_asset_limit(self):
        """Check the assets have not exceeded the limit"""
        model_number = self.asset.model_number
        available_assets = Asset.objects.filter(
            current_status="Available", model_number=model_number
        ).count()
        if available_assets <= int(os.environ.get("ASSET_LIMIT", 0)):
            message = "Warning!! The number of available {} ".format(
                model_number
            ) + " is {}".format(available_assets)
            slack.send_message(message)

    def _new_allocation_history_when_asset_is_made_available(self):
        try:
            last_allocation_record = AllocationHistory.objects.filter(
                asset=self.asset
            ).latest("created_at")
        except Exception as e:
            logger.warning(str(e))
        else:
            if self.current_status == constants.AVAILABLE and last_allocation_record:
                AllocationHistory.objects.create(
                    asset=self.asset,
                    previous_assignee=last_allocation_record.current_assignee,
                    current_assignee=None,
                )


class AllocationHistory(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.PROTECT)
    current_assignee = models.ForeignKey(
        "AssetAssignee",
        related_name="current_assignee_asset",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    previous_assignee = models.ForeignKey(
        "AssetAssignee",
        related_name="previous_assignee_asset",
        editable=False,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    assigner = models.ForeignKey(
        "User",
        related_name="asset_assigner",
        editable=False,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Allocation History"
        ordering = ["-id"]

    def clean(self):
        if self.asset.current_status != constants.AVAILABLE:
            raise ValidationError("You can only allocate available assets")

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            latest_record = AllocationHistory.objects.filter(asset=self.asset).latest(
                "created_at"
            )
            self.previous_assignee = latest_record.current_assignee
        except Exception:
            self.previous_assignee = None
        try:
            super().save(*args, **kwargs)
        except Exception:
            raise
        else:
            asset = self.asset
            asset.assigned_to = self.current_assignee
            asset.save()
            self._create_asset_status_when_asset_is_allocated()
            self._send_notification()

    def _create_asset_status_when_asset_is_allocated(self):
        last_status = AssetStatus.objects.filter(asset=self.asset).latest("created_at")
        if self.current_assignee:
            AssetStatus.objects.create(
                asset=self.asset,
                current_status=constants.ALLOCATED,
                previous_status=last_status.current_status,
            )

    def _send_notification(self):
        asset = self.asset
        assignee = None
        serial_no = asset.serial_number
        asset_code = asset.asset_code

        env_message = " *_(this is a test message.)_*" if settings.DEBUG else ""
        serial_no = f"Serial Number {serial_no} " if serial_no else ""
        asset_code = f"Asset Code {asset_code} " if asset_code else ""
        _and = f"and " if asset_code and serial_no else ""
        message = f"The {asset.asset_type} with {serial_no}{_and}{asset_code}"
        to_append = "Please contact the Ops team if this information is inaccurate."

        if asset.assigned_to and asset.current_status == constants.ALLOCATED:
            message += "has been allocated to you. {} {}".format(to_append, env_message)
            assignee = self.current_assignee
        elif not asset.assigned_to and self.previous_assignee:
            message += "has been de-allocated from you. {} {}".format(
                to_append, env_message
            )
            assignee = self.previous_assignee

        if assignee and hasattr(assignee, "email"):
            slack.send_message(message, user=assignee.user)


class AssetCondition(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.PROTECT)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Asset Condition"
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception:
            raise
        else:
            self._save_notes()

    def _save_notes(self):
        related_asset = self.asset
        if self.notes != related_asset.notes:
            related_asset.notes = self.notes
            related_asset.save()


class AssetIncidentReport(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.PROTECT)
    incident_type = models.CharField(max_length=50, choices=constants.INCIDENT_TYPES)
    incident_location = models.CharField(max_length=50)
    incident_description = models.TextField()
    injuries_sustained = models.TextField(null=True, blank=True)
    loss_of_property = models.TextField(null=True, blank=True)
    witnesses = models.TextField(null=True, blank=True)
    police_abstract_obtained = models.CharField(max_length=255)
    submitted_by = models.ForeignKey("User", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.incident_type}: {self.asset}"

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception:
            raise
        else:
            self._save_initial_incident_report_state()

    def _save_initial_incident_report_state(self):
        existing_state = StateTransition.objects.filter(asset_incident_report=self)
        if not existing_state:
            StateTransition.objects.create(
                asset_incident_report=self,
                incident_report_state=constants.NEWLY_REPORTED,
            )

        # user updates asset_status if lost
        if self.incident_type == "Loss":
            AssetStatus.objects.create(
                current_status=constants.LOST, asset_id=self.asset_id
            ).save()


class StateTransition(models.Model):
    asset_incident_report = models.ForeignKey(
        "AssetIncidentReport", on_delete=models.PROTECT
    )
    incident_report_state = models.CharField(
        max_length=50,
        choices=constants.REPORT_STATE_OPTIONS,
        default=constants.NEWLY_REPORTED,
    )
    asset_state_from_report = models.CharField(
        max_length=50,
        choices=constants.ASSET_STATE_FROM_REPORT_OPTIONS,
        default=constants.REQUIRES_REPAIR,
    )

    class Meta:
        verbose_name_plural = "State Transitions"

    def save(self, *args, **kwargs):

        # admin updates asset_status if damaged
        if self.asset_state_from_report == "Damaged":
            AssetStatus.objects.create(
                current_status=constants.DAMAGED,
                asset_id=self.asset_incident_report.asset_id,
            ).save()

        super().save(*args, **kwargs)
