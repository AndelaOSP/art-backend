# Standard Library
import logging

# Third-Party Imports
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from oauth2_provider.models import AbstractApplication

# App Imports
from core.constants import REPORT_TYPES

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, **fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = fields.pop("email")
        password = fields.get("password")
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, **fields):
        fields.setdefault("is_staff", False)
        fields.setdefault("is_superuser", False)

        return self._create_user(**fields)

    def create_superuser(self, **fields):
        fields.setdefault("is_staff", True)
        fields.setdefault("is_superuser", True)
        if fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(**fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=50, unique=True)
    cohort = models.IntegerField(blank=True, null=True)
    slack_id = models.CharField(max_length=50, blank=True, null=True)
    picture = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    location = models.ForeignKey(
        "AndelaCentre", blank=True, null=True, on_delete=models.PROTECT
    )
    is_securityuser = models.BooleanField(default=False)
    department = models.ForeignKey(
        "Department", null=True, blank=True, on_delete=models.PROTECT
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name_plural = "All Users"
        ordering = ["-id"]
        indexes = [models.Index(fields=["cohort"])]

    def clean(self):
        email_domain = self.email.split("@")[1]
        if "andela" not in email_domain.lower():
            raise ValidationError("Only andela email addresses allowed")

    def save(self, *args, **kwargs):
        self.clean()
        self.full_clean()
        try:
            super(User, self).save(*args, **kwargs)
        except Exception:
            raise
        else:
            self._create_assignee_object_for_user()

    def _create_assignee_object_for_user(self):
        from .asset import AssetAssignee

        AssetAssignee.objects.get_or_create(user=self)


class APIUser(AbstractApplication):
    client_type = models.CharField(
        max_length=32,
        choices=AbstractApplication.CLIENT_TYPES,
        default=AbstractApplication.CLIENT_CONFIDENTIAL,
    )
    authorization_grant_type = models.CharField(
        max_length=32,
        choices=AbstractApplication.GRANT_TYPES,
        default=AbstractApplication.GRANT_CLIENT_CREDENTIALS,
    )

    class Meta:
        verbose_name = "API User"
        ordering = ["-id"]


class UserFeedback(models.Model):
    """ Stores user feedback data """

    reported_by = models.ForeignKey("User", on_delete=models.PROTECT)
    message = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "User Feedback"
        ordering = ["-id"]


class AISUserSync(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    message = models.TextField()
    new_records = models.IntegerField(blank=True, null=True)
    running = models.BooleanField(default=False)
    running_time = models.DurationField(blank=True, null=True)
    successful = models.BooleanField(blank=True, null=True)
    updated_records = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "AIS User Sync"
        verbose_name_plural = "AIS User Sync"

    def __str__(self):
        result = "Unknown"
        if self.successful is not None:
            result = "Success" if self.successful else "Failure"
        return "Date ran: {}, Result: {}".format(self.created_at, result)
