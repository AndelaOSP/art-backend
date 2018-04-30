from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from oauth2_provider.models import AbstractApplication


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
