from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserChangeForm, UserCreationForm
from .models import (AssetCategory, AssetType,
                     AssetSubCategory, Item, AssetMake, ItemModelNumber)

User = get_user_model()

admin.site.register(
    [
        AssetCategory,
        AssetType,
        AssetSubCategory,
        Item,
        AssetMake,
        ItemModelNumber
    ]
)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'email', 'name', 'cohort', 'slack_handle', 'admin'
    )
    list_filter = (
        'cohort', 'admin'
    )

    fieldsets = (
        ('Account', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'cohort',
                                      'slack_handle',
                                      'picture',
                                      'phone_number')}),
        ('Permissions', {'fields': ('admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name',
                       'cohort', 'slack_handle',
                       'password1', 'password2')
        }),
    )

    ordering = (
        'email', 'name', 'cohort', 'slack_handle'
    )
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
