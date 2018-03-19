from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager


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
    item_code = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('User', blank=True,
                                    on_delete=models.PROTECT)
    model_number = models.ForeignKey(ItemModelNumber, null=True,
                                     on_delete=models.PROTECT)

    def clean(self):
        if not self.item_code and not self.serial_number:
            raise ValidationError(('Please provide either the serial number,\
                               asset code or both.'), code='required')

    def save(self, *args, **kwargs):
        """Validate either item code or serial number are provided"""
        if not self.item_code and not self.serial_number:
            self.full_clean()
        else:
            super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return '{}{}{}'.format(self.item_code, self.serial_number,
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


class SecurityUser(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=12)
    security_badge_number = models.CharField(max_length=30, unique=True)
