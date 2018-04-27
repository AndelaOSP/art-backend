from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserRegistrationForm
from .models import (AssetCategory, AssetType,
                     AssetSubCategory,
                     Asset,
                     AssetMake,
                     AssetModelNumber,
                     SecurityUser,
                     AssetLog,
                     AssetStatus,
                     UserFeedback,
                     AllocationHistory)

User = get_user_model()

admin.site.register(
    [
        AssetCategory,
        AssetType,
        AssetSubCategory,
        AssetMake,
        AssetModelNumber,
        AssetLog
    ]
)


class SecurityUserAdmin(BaseUserAdmin):
    add_form = UserRegistrationForm
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
    add_form = UserRegistrationForm
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


class AssetAdmin(admin.ModelAdmin):
    list_filter = (
        'model_number', 'model_number__make_label__asset_type__asset_type'
    )
    list_display = (
        'asset_code', 'serial_number', 'model_number', 'created_at',
        'assigned_to', 'current_status'
    )


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ('asset', 'current_status', 'previous_status', 'created_at')


class UserFeedbackAdmin(admin.ModelAdmin):
    list_filter = ('report_type',)
    list_display = ('message', 'report_type', 'reported_by')


class AllocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'current_owner', 'previous_owner', 'created_at')


admin.site.register(Asset, AssetAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(SecurityUser, SecurityUserAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(AllocationHistory, AllocationHistoryAdmin)
