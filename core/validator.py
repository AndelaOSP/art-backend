import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_date(value):
    if value > datetime.date.today():
        raise ValidationError(
            _('%(value)s invalid purchase date'), params={'value': value},
        )
