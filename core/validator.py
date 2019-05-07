# Standard Library
import datetime

# Third-Party Imports
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_date(value):
    if value > datetime.date.today():
        raise ValidationError(
            _(
                "%(value)s is invalid. Purchase date can only be today or a date in the past"
            ),
            params={"value": value},
        )
