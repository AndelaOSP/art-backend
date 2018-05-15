from django.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save

from .user import SecurityUser

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


class AssetCategory(models.Model):
    """ Stores all asset categories """
    category_name = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.category_name


class AssetSubCategory(models.Model):
    """Stores all asset sub categories"""
    sub_category_name = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)
    asset_category = models.ForeignKey(AssetCategory,
                                       on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = 'Asset SubCategories'

    def __str__(self):
        return self.sub_category_name


class AssetType(models.Model):
    """Stores all asset types"""
    asset_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    asset_sub_category = models.ForeignKey(AssetSubCategory,
                                           on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Asset Type"

    def __str__(self):
        return self.asset_type


class AssetMake(models.Model):
    """ stores all asset makes """
    make_label = models.CharField(
        max_length=40, null=False, verbose_name="Asset Make")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Asset Make"

    def __str__(self):
        return self.make_label


class AssetModelNumber(models.Model):
    model_number = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    make_label = models.ForeignKey(AssetMake,
                                   null=True,
                                   on_delete=models.PROTECT,
                                   verbose_name="Asset Make")

    class Meta:
        verbose_name = "Asset Model Number"

    def __str__(self):
        return self.model_number


class Asset(models.Model):
    """Stores all assets"""
    asset_code = models.CharField(unique=True, max_length=50)
    serial_number = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('User',
                                    blank=True,
                                    editable=False,
                                    null=True,
                                    on_delete=models.PROTECT)
    model_number = models.ForeignKey(AssetModelNumber,
                                     null=True,
                                     on_delete=models.PROTECT)
    current_status = models.CharField(editable=False, max_length=50)
    asset_condition = models.CharField(editable=False,
                                       max_length=50,
                                       default='Brand New')

    def clean(self):
        if not self.asset_code and not self.serial_number:
            raise ValidationError(('Please provide either the serial number,\
                               asset code or both.'), code='required')

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


class AssetLog(models.Model):
    """Stores checkin/Checkout asset logs"""
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
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


class AssetStatus(models.Model):
    """Stores the previous and current status of models"""
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
                              null=False,
                              on_delete=models.PROTECT)

    current_status = models.CharField(max_length=50,
                                      choices=ASSET_STATUSES)
    previous_status = models.CharField(max_length=50, choices=ASSET_STATUSES,
                                       null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Statuses'

    def save(self, *args, **kwargs):
        try:
            latest_record = AssetStatus.objects.filter(asset=self.asset).\
                latest('created_at')
            self.previous_status = latest_record.current_status
        except Exception:
            self.previous_status = None
        self.full_clean()
        super(AssetStatus, self).save(*args, **kwargs)


class AllocationHistory(models.Model):
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
                              null=False,
                              on_delete=models.PROTECT)
    current_owner = models.ForeignKey('User',
                                      related_name='current_owner_asset',
                                      blank=True,
                                      null=True,
                                      on_delete=models.PROTECT)
    previous_owner = models.ForeignKey('User',
                                       related_name='previous_owner_asset',
                                       editable=False,
                                       blank=True,
                                       null=True,
                                       on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "Allocation History"

    def clean(self):
        if self.asset.current_status != AVAILABLE:
            raise ValidationError("You can only allocate available assets")

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            latest_record = AllocationHistory.objects.\
                filter(asset=self.asset).latest('created_at')
            self.previous_owner = latest_record.current_owner
        except Exception:
            self.previous_owner = None
        super(AllocationHistory, self).save(*args, **kwargs)


class AssetCondition(models.Model):
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
                              null=False,
                              on_delete=models.PROTECT)

    asset_condition = models.CharField(max_length=50,
                                       editable=True,
                                       blank=True,
                                       null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Asset Condition'

    def save(self, *args, **kwargs):
        super(AssetCondition, self).save(*args, **kwargs)


@receiver(post_save, sender=AssetStatus)
def set_current_asset_status(sender, **kwargs):
    asset_status = kwargs.get('instance')
    asset_status.asset.current_status = asset_status.current_status
    if asset_status.current_status == AVAILABLE and AllocationHistory.\
            objects.count() > 0:
        asset_status.asset.assigned_to = None
        AllocationHistory.objects.create(asset=asset_status.asset,
                                         current_owner=None)
    asset_status.asset.save()


@receiver(post_save, sender=Asset)
def save_initial_asset_status(sender, **kwargs):
    current_asset = kwargs.get('instance')
    existing_status = AssetStatus.objects.filter(asset=current_asset)
    if not existing_status:
        current_asset.current_status = AVAILABLE
        AssetStatus.objects.create(asset=current_asset,
                                   current_status=AVAILABLE)
        current_asset.save()


@receiver(post_save, sender=AssetCondition)
def save_asset_condition(sender, **kwargs):
    new_condition = kwargs.get('instance')
    related_asset = new_condition.asset
    if not new_condition.asset_condition == \
            related_asset.asset_condition:
        related_asset.asset_condition = \
            new_condition.asset_condition
        related_asset.save()


@receiver(post_save, sender=AllocationHistory)
def save_current_asset_owner(sender, **kwargs):
    asset_owner = kwargs.get('instance')
    asset_owner.asset.assigned_to = asset_owner.current_owner
    asset_owner.asset.save()
