# Standard Library
import threading

# Third-Party Imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.management import call_command

# App Imports
from core import models

from .forms import UserRegistrationForm, UserSyncForm

admin.site.register(
    [
        models.AndelaCentre,
        models.AssetCategory,
        models.AssetIncidentReport,
        models.AssetMake,
        models.AssetModelNumber,
        models.AssetSpecs,
        models.AssetSubCategory,
        models.AssetType,
        models.Country,
        models.OfficeBlock,
        models.StateTransition,
    ]
)


class UserAdmin(BaseUserAdmin):
    add_form = UserRegistrationForm
    search_fields = ("email", "first_name", "last_name")
    list_display = (
        "email",
        "cohort",
        "location",
        "is_active",
        "is_securityuser",
        "last_modified",
    )
    list_filter = ("cohort",)

    fieldsets = (
        ("Account", {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "cohort",
                    "slack_id",
                    "phone_number",
                    "picture",
                    "is_staff",
                    "is_superuser",
                    "is_securityuser",
                    "location",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "cohort",
                    "phone_number",
                    "is_staff",
                    "is_superuser",
                    "picture",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    ordering = ("email", "cohort")


class AssetAdmin(admin.ModelAdmin):
    list_filter = (
        "model_number",
        "model_number__asset_make__asset_type__name",
        "purchase_date",
        "verified",
    )
    list_display = (
        "uuid",
        "asset_code",
        "serial_number",
        "model_number",
        "created_at",
        "assigned_to",
        "current_status",
        "notes",
        "purchase_date",
        "verified",
        "asset_location",
    )


class AISUserSyncAdmin(admin.ModelAdmin):
    form = UserSyncForm
    list_filter = ("running_time", "successful", "created_at")
    list_display = (
        "running_time",
        "successful",
        "new_records",
        "updated_records",
        "created_at",
    )

    def save_model(self, request, obj, form, change):
        if change:
            return super(AISUserSyncAdmin, self).save_model(request, obj, form, change)
        else:
            t = threading.Thread(target=call_command, args=("sync_users",))
            t.setDaemon(True)
            t.start()

    def get_fields(self, request, obj=None):
        fields = super(AISUserSyncAdmin, self).get_fields(request, obj)
        if obj:
            fields.remove("new_sync")
            return fields
        return ["new_sync"]


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ("asset", "current_status", "previous_status", "created_at")


class UserFeedbackAdmin(admin.ModelAdmin):
    list_filter = ("report_type",)
    list_display = ("message", "report_type", "reported_by")


class AllocationHistoryAdmin(admin.ModelAdmin):
    list_display = ("asset", "current_assignee", "previous_assignee", "created_at")


class AssetConditionAdmin(admin.ModelAdmin):
    list_display = ("asset", "notes", "created_at")


class AssetLogsAdmin(admin.ModelAdmin):
    list_display = ("created_at", "asset", "checked_by", "log_type")


class OfficeFloorAdmin(admin.ModelAdmin):
    list_filter = ("block",)
    list_display = ("number", "block")


class OfficeFloorSectionAdmin(admin.ModelAdmin):
    list_filter = ("floor", "floor__block")
    list_display = ("name", "floor")


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "last_modified")


class OfficeWorkspaceAdmin(admin.ModelAdmin):
    list_display = ("section", "name")


admin.site.register(models.AISUserSync, AISUserSyncAdmin)
admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.AssetLog, AssetLogsAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AssetStatus, AssetStatusAdmin)
admin.site.register(models.UserFeedback, UserFeedbackAdmin)
admin.site.register(models.AllocationHistory, AllocationHistoryAdmin)
admin.site.register(models.AssetCondition, AssetConditionAdmin)
admin.site.register(models.OfficeFloor, OfficeFloorAdmin)
admin.site.register(models.OfficeFloorSection, OfficeFloorSectionAdmin)
admin.site.register(models.OfficeWorkspace, OfficeWorkspaceAdmin)
admin.site.register(models.Department, DepartmentAdmin)
