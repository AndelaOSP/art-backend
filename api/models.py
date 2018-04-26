from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from oauth2_provider.models import AbstractApplication


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
    current_owner = models.ForeignKey('User',
                                      blank=True,
                                      editable=False,
                                      null=True,
                                      on_delete=models.PROTECT)
    model_number = models.ForeignKey(AssetModelNumber, null=True,
                                     on_delete=models.PROTECT)
    current_status = models.CharField(editable=False, max_length=50)

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


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, **fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = fields.pop('email')
        password = fields.get('password')
        cohort = fields.get('cohort')
        slack_handle = fields.get('slack_handle')
        if not email:
            raise ValueError("Email address is required")
        elif not cohort:
            raise ValueError("Cohort is required")
        elif not slack_handle:
            raise ValueError("Slack handle is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, **fields):
        fields.setdefault('is_staff', False)
        fields.setdefault('is_superuser', False)

        return self._create_user(**fields)

    def create_superuser(self, **fields):
        fields.setdefault('is_staff', True)
        fields.setdefault('is_superuser', True)

        if fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(**fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=50, unique=True)
    cohort = models.IntegerField(blank=True, null=True)
    slack_handle = models.CharField(max_length=50,
                                    blank=True, null=True)
    picture = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cohort', 'slack_handle']
    objects = UserManager()

    class Meta:
        verbose_name_plural = "All Users"


class SecurityUser(User):
    badge_number = models.CharField(max_length=30, unique=True)

    USERNAME_FIELD = 'badge_number'
    REQUIRED_FIELDS = ['first_name', 'last_name',
                       'badge_number']

    class Meta:
        verbose_name = "Security User"


class APIUser(AbstractApplication):
    client_type = models.CharField(
        max_length=32,
        choices=AbstractApplication.CLIENT_TYPES,
        default=AbstractApplication.CLIENT_CONFIDENTIAL)
    authorization_grant_type = models.CharField(
        max_length=32,
        choices=AbstractApplication.GRANT_TYPES,
        default=AbstractApplication.GRANT_CLIENT_CREDENTIALS
    )

    class Meta:
        verbose_name = "API User"


class AssetLog(models.Model):
    """Stores checkin/Checkout asset logs"""
    CHECKIN = "Checkin"
    CHECKOUT = "Checkout"
    REQUIRED_FIELDS = ['checkin', 'checkout']

    option = (
        (CHECKIN, "Checkin"),
        (CHECKOUT, "Checkout"),
    )
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
                              null=False,
                              on_delete=models.PROTECT)
    checked_by = models.ForeignKey(SecurityUser,
                                   blank=True,
                                   on_delete=models.PROTECT)
    log_type = models.CharField(max_length=10,
                                blank=False,
                                choices=option)
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


class UserFeedback(models.Model):
    """ Stores user feedback data """
    FEEDBACK = "feedback"
    BUG = "bug"
    option = (
        (FEEDBACK, "feedback"),
        (BUG, "bug"),
    )
    reported_by = models.ForeignKey(User, on_delete=models.PROTECT)
    message = models.CharField(max_length=200, null=False)
    report_type = models.CharField(max_length=10,
                                   blank=False,
                                   choices=option,
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "User Feedback"


class AssetStatus(models.Model):
    """Stores the previous and current status of models"""
    AVAILABLE = "Available"
    ALLOCATED = "Allocated"
    LOST = "Lost"
    DAMAGED = "Damaged"

    asset_statuses = (
        (AVAILABLE, "Available"),
        (ALLOCATED, "Allocated"),
        (LOST, "Lost"),
        (DAMAGED, "Damaged")
    )
    asset = models.ForeignKey(Asset,
                              to_field="serial_number",
                              null=False,
                              on_delete=models.PROTECT)

    current_status = models.CharField(max_length=50,
                                      choices=asset_statuses)
    previous_status = models.CharField(max_length=50, choices=asset_statuses,
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
        verbose_name_plural = "Allocation Histories"

    def clean(self):
        if self.asset.current_status != "Available":
            raise ValidationError("You can only allocate available assets")

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            latest_record = AllocationHistory.objects.filter(asset=self.asset).\
                latest('created_at')
            self.previous_owner = latest_record.current_owner
        except Exception:
            self.previous_owner = None
        super(AllocationHistory, self).save(*args, **kwargs)


@receiver(post_save, sender=AssetStatus)
def set_current_asset_status(sender, **kwargs):
    asset_status = kwargs.get('instance')
    asset_status.asset.current_status = asset_status.current_status
    asset_status.asset.save()


@receiver(post_save, sender=Asset)
def save_initial_asset_status(sender, **kwargs):
    current_asset = kwargs.get('instance')
    existing_status = AssetStatus.objects.filter(asset=current_asset)
    if not existing_status:
        current_asset.current_status = "Available"
        AssetStatus.objects.create(asset=current_asset,
                                   current_status="Available")
        current_asset.save()


@receiver(post_save, sender=AllocationHistory)
def save_current_asset_owner(sender, **kwargs):
    asset_owner = kwargs.get('instance')
    asset_owner.asset.current_owner = asset_owner.current_owner
    asset_owner.asset.save()
