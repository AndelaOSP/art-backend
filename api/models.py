from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
    def create_user(self, email, name, cohort, slack_handle,
                    is_active=True, is_admin=False, is_staff=False,
                    phone_number=None, picture=None, password=None):
        if not email:
            raise ValueError("Email address is required")
        elif not name:
            raise ValueError("Name is required")
        elif not cohort:
            raise ValueError("Cohort is required")
        elif not slack_handle:
            raise ValueError("Slack handle is required")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            cohort=cohort,
            slack_handle=slack_handle,
        )

        user.set_password(password)
        user.picture = picture
        user.staff = is_staff
        user.admin = is_admin
        user.active = is_active
        user.phone_number = phone_number
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, name, cohort,
                         slack_handle, password=None):
        user = self.create_user(
            email=email,
            name=name,
            cohort=cohort,
            slack_handle=slack_handle,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, email, name, cohort,
                         slack_handle, password=None):
        user = self.create_user(
            email=email,
            name=name,
            cohort=cohort,
            slack_handle=slack_handle,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    cohort = models.IntegerField(blank=True, null=True)
    slack_handle = models.CharField(max_length=50, unique=True,
                                    blank=True, null=True)
    picture = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cohort', 'slack_handle']
    objects = UserManager()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    def __str__(self):
        return self.email
