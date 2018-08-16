from django.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime

from .department import Department
from .officeblock import OfficeWorkspace
from .user import SecurityUser, User
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
    sub_category_name = models.CharField(
        unique=True, max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)
    asset_category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT
    )

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
    make_label = models.CharField(unique=True, max_length=40,
                                  null=False, verbose_name="Asset Make")
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
    make_label = models.ForeignKey(AssetMake,
                                   null=True,
                                   on_delete=models.PROTECT,
                                   verbose_name="Asset Make")
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
    year_of_manufacture = models.IntegerField(null=True,
                                              blank=True,
                                              choices=YEAR_CHOICES)
    processor_type = models.CharField(max_length=300,
                                      blank=True,
                                      null=True,
                                      choices=PROCESSOR_TYPE)
    processor_speed = models.FloatField(null=True,
                                        blank=True,
                                        choices=PROCESSOR_SPEED)
    screen_size = models.IntegerField(null=True,
                                      blank=True,
                                      choices=SCREEN_SIZES)
    storage = models.IntegerField(null=True,
                                  blank=True,
                                  choices=STORAGE_SIZES)
    memory = models.IntegerField(null=True,
                                 blank=True,
                                 choices=MEMORY)

    class Meta:
        verbose_name = "Asset Specification"
        unique_together = ("storage", "memory",
                           "screen_size", "processor_speed",
                           "year_of_manufacture", "processor_type")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.memory}GB RAM, " \
               f"{self.storage}GB, " \
               f"{self.processor_speed}GHz," \
               f"{self.screen_size}\""


class Asset(models.Model):
    """Stores all assets"""
    asset_code = models.CharField(
        unique=True, null=True, blank=True, max_length=50)
    serial_number = models.CharField(
        unique=True, null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    purchase_date = models.DateField(
        validators=[validate_date],
        null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('AssetAssignee',
                                    blank=True,
                                    editable=False,
                                    null=True,
                                    on_delete=models.PROTECT)
    model_number = models.ForeignKey(AssetModelNumber,
                                     null=True,
                                     on_delete=models.PROTECT)
    current_status = models.CharField(editable=False, max_length=50)
    notes = models.TextField(editable=False, default=" ", )
    specs = models.ForeignKey(
        AssetSpecs,
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
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
        super(Asset, self).save(*args, **kwargs)

    def __str__(self):
        return '{}, {}, {}'.format(self.asset_code,
                                   self.serial_number,
                                   self.model_number)

    class Meta:
        ordering = ['-id']
        unique_together = ("asset_code", "serial_number",)


class AssetAssignee(models.Model):
    department = models.OneToOneField('Department', null=True, blank=True,
                                      on_delete=models.CASCADE)
    workspace = models.OneToOneField(
        'OfficeWorkspace',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    user = models.OneToOneField('User', null=True, blank=True,
                                on_delete=models.CASCADE)

    def __str__(self):
        assignee = self.workspace or self.department or self.user
        if assignee:
            return str(assignee)
        else:
            raise ValidationError(
                message="No Department, Workspace or"
                        " User for this AssetAssignee")

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
    asset = models.ForeignKey(Asset,
                              null=False,
                              on_delete=models.PROTECT)
    checked_by = models.ForeignKey(SecurityUser,
                                   blank=True,
                                   on_delete=models.PROTECT)
    log_type = models.CharField(max_length=10,
                                blank=False,
                                choices=LOG_TYPE_CHOICES)
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
    asset = models.ForeignKey(Asset,
                              null=False,
                              on_delete=models.PROTECT)

    current_status = models.CharField(max_length=50,
                                      choices=ASSET_STATUSES,
                                      default=ASSET_STATUSES[0][0])
    previous_status = models.CharField(max_length=50, choices=ASSET_STATUSES,
                                       null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Statuses'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        try:
            latest_record = AssetStatus.objects.filter(asset=self.asset). \
                latest('created_at')
            self.previous_status = latest_record.current_status
        except Exception:
            self.previous_status = None
        self.full_clean()
        super(AssetStatus, self).save(*args, **kwargs)


class AllocationHistory(models.Model):
    asset = models.ForeignKey(Asset,
                              null=False,
                              on_delete=models.PROTECT)
    current_owner = models.ForeignKey('AssetAssignee',
                                      related_name='current_owner_asset',
                                      blank=True,
                                      null=True,
                                      on_delete=models.PROTECT)
    previous_owner = models.ForeignKey('AssetAssignee',
                                       related_name='previous_owner_asset',
                                       editable=False,
                                       blank=True,
                                       null=True,
                                       on_delete=models.PROTECT)
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
            latest_record = AllocationHistory.objects. \
                filter(asset=self.asset).latest('created_at')
            self.previous_owner = latest_record.current_owner
        except Exception:
            self.previous_owner = None
        super(AllocationHistory, self).save(*args, **kwargs)


class AssetCondition(models.Model):
    asset = models.ForeignKey(Asset,
                              null=False,
                              on_delete=models.PROTECT)

    notes = models.TextField(editable=True,
                             blank=True,
                             null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Condition'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        super(AssetCondition, self).save(*args, **kwargs)


class AssetIncidentReport(models.Model):
    asset = models.ForeignKey(Asset,
                              null=False,
                              on_delete=models.PROTECT)
    incident_type = models.CharField(max_length=50,
                                     choices=INCIDENT_TYPES)
    incident_location = models.CharField(max_length=50,
                                         null=False,
                                         blank=False)
    incident_description = models.TextField(null=False,
                                            blank=False)
    injuries_sustained = models.TextField(null=True,
                                          blank=True)
    loss_of_property = models.TextField(null=True,
                                        blank=True)
    witnesses = models.TextField(null=True,
                                 blank=True)
    police_abstract_obtained = models.CharField(max_length=255,
                                                blank=False,
                                                null=False)
    submitted_by = models.ForeignKey('User',
                                     blank=False,
                                     null=True,
                                     on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.incident_type}: {self.asset}"

    class Meta:
        ordering = ['-id']


@receiver(post_save, sender=AssetStatus)
def set_current_asset_status(sender, **kwargs):
    asset_status = kwargs.get('instance')
    asset_status.asset.current_status = asset_status.current_status
    if asset_status.current_status == AVAILABLE:
        asset_status.asset.assigned_to = None
    asset_status.asset.save()


@receiver(post_save, sender=AssetStatus)
def check_asset_limit(sender, **kwargs):
    """Check the assets have not exceeded the limit"""
    asset_status = kwargs.get('instance')
    model_number = asset_status.asset.model_number
    available_assets = Asset.objects.filter(
        current_status='Available', model_number=model_number
    ).count()
    if available_assets <= 10:
        message = "Warning!! The number of available {} ".format(
            model_number) + " is {}".format(available_assets)
        slack.send_message(message)


@receiver(post_save, sender=Asset)
def save_initial_asset_status(sender, **kwargs):
    current_asset = kwargs.get('instance')
    existing_status = AssetStatus.objects.filter(asset=current_asset)
    if current_asset and not existing_status:
        AssetStatus.objects.create(asset=current_asset,
                                   current_status=AVAILABLE)
        current_asset.current_status = AVAILABLE
        current_asset.save()


@receiver(post_save, sender=AssetCondition)
def save_notes(sender, **kwargs):
    new_condition = kwargs.get('instance')
    related_asset = new_condition.asset
    if not new_condition.notes == related_asset.notes:
        related_asset.notes = \
            new_condition.notes
        related_asset.save()


@receiver(post_save, sender=AllocationHistory)
def update_asset_status_when_allocation_changes(sender, **kwargs):
    allocation_history = kwargs.get('instance')

    if kwargs.get('created'):
        last_status = \
            AssetStatus.objects.filter(
                asset=allocation_history.asset).latest('created_at')
        if allocation_history.current_owner:
            AssetStatus.objects.create(
                asset=allocation_history.asset,
                current_status=ALLOCATED,
                previous_status=last_status.current_status
            )


@receiver(post_save, sender=AssetStatus)
def update_asset_allocation_history_when_status_changes(sender, **kwargs):
    asset_status = kwargs.get('instance')

    if kwargs.get('created'):
        try:
            last_allocation_record = \
                AllocationHistory.objects.filter(
                    asset=asset_status.asset).latest('created_at')
        except Exception:
            return
        if asset_status.current_status == AVAILABLE \
                and last_allocation_record:
            AllocationHistory.objects.create(
                asset=asset_status.asset,
                previous_owner=last_allocation_record.current_owner,
                current_owner=None)


@receiver(post_save, sender=AllocationHistory)
def allocation_history_post_save(sender, **kwargs):
    allocation_history = kwargs.get('instance')
    asset = allocation_history.asset
    owner = allocation_history.current_owner
    asset.assigned_to = owner
    asset.save()

    if asset.assigned_to and asset.current_status == AVAILABLE:
        message = "The asset with serial number {} ".format(
            asset.serial_number) + "has been allocated to you."
        # send slack message only to user
        if hasattr(owner.user, 'email'):
            slack.send_message(message, user=owner.user)
        asset_status = AssetStatus.objects.create(
            asset=asset,
            current_status=ALLOCATED
        )
        asset_status.save()


@receiver(post_save, sender=User)
def assetassignee_user(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'assetassignee'):
        AssetAssignee.objects.create(user=instance)
    instance.assetassignee.save()


@receiver(post_save, sender=Department)
def assetassignee_department(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'assetassignee'):
        AssetAssignee.objects.create(department=instance)
    instance.assetassignee.save()


@receiver(post_save, sender=OfficeWorkspace)
def assetassignee_workspace(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'assetassignee'):
        AssetAssignee.objects.create(workspace=instance)
    instance.assetassignee.save()
