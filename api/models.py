from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
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

    def __str__(self):
        return self.asset_type


class AssetMake(models.Model):
    """ stores all asset makes """
    make_label = models.CharField(max_length=40, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, editable=False)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)

    def __str__(self):
        return self.make_label


class ItemModelNumber(models.Model):
    model_number = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    make_label = models.ForeignKey(AssetMake,
                                   null=True,
                                   on_delete=models.PROTECT)

    def __str__(self):
        return self.model_number


class Item(models.Model):
    """Stores all items"""

    AVAILABLE = "Available"
    ALLOCATED = "Allocated"
    LOST = "Lost"
    DAMAGED = "Damaged"

    item_statuses = (
        (AVAILABLE, "Available"),
        (ALLOCATED, "Allocated"),
        (LOST, "Lost"),
        (DAMAGED, "Damaged")
    )

    item_code = models.CharField(unique=True, max_length=50)
    serial_number = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('User',
                                    blank=True,
                                    null=True,
                                    on_delete=models.PROTECT)
    model_number = models.ForeignKey(ItemModelNumber, null=True,
                                     on_delete=models.PROTECT)
    allocation_status = models.CharField(max_length=9,
                                         choices=item_statuses,
                                         default="Available")

    def clean(self):
        if not self.item_code and not self.serial_number:
            raise ValidationError(('Please provide either the serial number,\
                               asset code or both.'), code='required')

        elif self.allocation_status not in dict(self.item_statuses):
            raise ValueError('Status provided does not exist')

    def save(self, *args, **kwargs):
        """
        Validate either item code, serial number
        are provided and an existing status is given
        """
        self.full_clean()
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return '{}, {}, {}'.format(self.item_code,
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
    asset = models.ForeignKey(Item,
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


class UserFeedback(models.Model):
    """ Stores user feedback data """
    FEEDBACK = "feedback"
    BUG = "bug"
    option = (
        (FEEDBACK, "feedback"),
        (BUG, "bug"),
    )
    reported_by = models.EmailField(max_length=50, unique=False, null=False)
    message = models.CharField(max_length=100, unique=False, null=False)
    report_type = models.CharField(max_length=10,
                                   blank=False,
                                   choices=option,
                                   null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
