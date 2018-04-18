from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (AssetCategory, AssetType,
                     AssetSubCategory,
                     Asset,
                     AssetMake,
                     AssetModelNumber,
                     SecurityUser,
                     AssetLog
                     )

User = get_user_model()

admin.site.register(
    [
        AssetCategory,
        AssetType,
        AssetSubCategory,
        Asset,
        AssetMake,
        AssetModelNumber,
        AssetLog,
    ]
)


class SecurityUserAdmin(BaseUserAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'badge_number',
        'phone_number',
    )

    list_filter = (
        'badge_number',
    )

    fieldsets = (
        ('Account', {'fields': ('first_name',
                                'last_name',
                                'email',
                                'badge_number',
                                'phone_number',
                                'password')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name',
                       'last_name',
                       'email',
                       'badge_number',
                       'phone_number',
                       'password1',
                       'password2')
        }),
    )

    ordering = (
        'first_name', 'last_name', 'badge_number'
    )


class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'cohort', 'slack_handle'
    )
    list_filter = (
        'cohort',
    )

    fieldsets = (
        ('Account', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name',
            'cohort', 'slack_handle',
            'phone_number', 'picture',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name',
                       'last_name', 'cohort',
                       'slack_handle', 'phone_number',
                       'picture', 'password1',
                       'password2')
        }),
    )

    ordering = (
        'email', 'cohort', 'slack_handle'
    )


admin.site.register(User, UserAdmin)
admin.site.register(SecurityUser, SecurityUserAdmin)
