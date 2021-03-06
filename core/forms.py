# Third-Party Imports
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

# App Imports
from core.models import AISUserSync


class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        required=False,
    )


class UserSyncForm(forms.ModelForm):
    new_sync = forms.CharField(
        label="Click Save to sync users",
        required=False,
        widget=forms.TextInput(attrs={"hidden": "true"}),
    )

    class Meta:
        model = AISUserSync
        fields = "__all__"
