# Standard Library
import functools
import logging
import operator

# Third-Party Imports
from django.db.models import Q
from django_filters import rest_framework as filters

# App Imports
from core.models import AllocationHistory, Asset, AssetLog, User

logger = logging.getLogger(__name__)

NULL_VALUE = "unspecified"


class BaseFilter(filters.FilterSet):
    def filter_contains_with_multiple_query_values(self, queryset, name, value):
        options = set(value.split(","))
        null_lookup = {}
        if NULL_VALUE in options:
            options.remove(NULL_VALUE)
            null_lookup = {"__".join([name, "isnull"]): True}
        if options:
            lookup = functools.reduce(
                operator.or_,
                {Q(**{"__".join([name, "icontains"]): item}) for item in options},
            )
        else:
            lookup = Q(**{})

        return queryset.filter(Q(lookup | Q(**null_lookup)))

    def filter_exact_with_multiple_query_values(self, queryset, name, value):
        options = set(value.split(","))
        null_lookup = {}
        if NULL_VALUE in options:
            options.remove(NULL_VALUE)
            null_lookup = {"__".join([name, "isnull"]): True}
        lookup = {"__".join([name, "in"]): options}
        return queryset.filter(Q(**lookup) | Q(**null_lookup))


class AssetFilter(BaseFilter):
    email = filters.CharFilter(
        field_name="assigned_to__user__email", lookup_expr="icontains"
    )
    model_number = filters.CharFilter(
        field_name="model_number__name",
        method="filter_contains_with_multiple_query_values",
    )
    asset_code = filters.CharFilter(
        field_name="asset_code",
        lookup_expr="icontains",
        method="filter_contains_with_multiple_query_values",
    )
    serial_number = filters.CharFilter(
        field_name="serial_number",
        lookup_expr="icontains",
        method="filter_contains_with_multiple_query_values",
    )
    asset_type = filters.CharFilter(
        field_name="model_number__asset_make__asset_type__name",
        method="filter_contains_with_multiple_query_values",
    )
    current_status = filters.CharFilter(
        field_name="current_status", lookup_expr="iexact"
    )
    verified = filters.CharFilter(field_name="verified", lookup_expr="iexact")
    department = filters.CharFilter(
        field_name="assigned_to__department__id", lookup_expr="iexact"
    )

    class Meta:
        model = Asset
        fields = ["asset_type", "model_number", "email", "current_status", "verified"]


class AssetLogFilter(BaseFilter):
    """Filters asset logs by specified fields"""

    # filters asset logs by asset type
    asset_type = filters.CharFilter(
        field_name="asset__model_number__asset_make__asset_type__name",
        lookup_expr="iexact",
    )
    asset_serial = filters.CharFilter(
        field_name="asset__serial_number", lookup_expr="iexact"
    )
    asset_code = filters.CharFilter(
        field_name="asset__asset_code", lookup_expr="iexact"
    )

    # filters asset logs by year
    year = filters.NumberFilter(field_name="created_at", lookup_expr="year")

    # filters asset logs by month
    month = filters.NumberFilter(field_name="created_at", lookup_expr="month")

    # filters asset logs by day
    day = filters.NumberFilter(field_name="created_at", lookup_expr="day")

    # filters asset logs by user/owner of the asset
    user = filters.CharFilter(
        field_name="asset__assigned_to__user__email", lookup_expr="icontains"
    )

    # filter asset logs by checked_by
    checked_by = filters.CharFilter(
        field_name="checked_by__email", lookup_expr="icontains"
    )
    asset_category = filters.CharFilter(
        field_name="asset__model_number__asset_make__asset_type__asset_sub_category__asset_category__name",
        lookup_expr="iexact",
    )
    asset_sub_category = filters.CharFilter(
        field_name="asset__model_number__asset_make__asset_type__asset_sub_category__name",
        lookup_expr="iexact",
    )
    asset_make = filters.CharFilter(
        field_name="asset__model_number__asset_make__name", lookup_expr="iexact"
    )

    class Meta:
        model = AssetLog
        fields = [
            "asset_type",
            "asset_serial",
            "asset_code",
            "user",
            "checked_by",
            "year",
            "month",
            "day",
            "asset_category",
            "asset_sub_category",
            "asset_make",
        ]


class UserFilter(BaseFilter):
    cohort = filters.CharFilter(
        field_name="cohort",
        lookup_expr="iexact",
        method="filter_exact_with_multiple_query_values",
    )
    email = filters.CharFilter(field_name="email", lookup_expr="istartswith")
    asset_count = filters.CharFilter(
        field_name="allocated_asset_count",
        label="Asset count",
        lookup_expr="iexact",
        method="filter_by_allocated_asset_count",
    )
    is_active = filters.CharFilter(field_name="is_active", lookup_expr="iexact")

    def filter_by_allocated_asset_count(self, queryset, name, value):
        users = [
            user.id
            for user in queryset
            if str(user.assetassignee.asset_set.count()) in value.split(",")
        ]
        return queryset.filter(id__in=users)

    class Meta:
        model = User
        fields = ["cohort", "email", "asset_count"]


class AllocationsHistoryFilter(BaseFilter):
    """Filters the allocations"""

    owner = filters.CharFilter(
        field_name="current_assignee__user__email", lookup_expr="icontains"
    )
    workspace = filters.CharFilter(
        field_name="current_assignee__workspace__id", lookup_expr="iexact"
    )
    department = filters.CharFilter(
        field_name="current_assignee__department__id", lookup_expr="iexact"
    )
    asset_serial_number = filters.CharFilter(
        field_name="asset__serial_number", lookup_expr="iexact"
    )
    asset_code = filters.CharFilter(
        field_name="asset__asset_code", lookup_expr="iexact"
    )

    class Meta:
        model = AllocationHistory
        fields = [
            "owner",
            "workspace",
            "department",
            "asset_serial_number",
            "asset_code",
        ]
