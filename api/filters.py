# Standard Library
import logging

# Third-Party Imports
from django.db.models import Q
from django_filters import rest_framework as filters

# App Imports
from core.models import Asset, User

logger = logging.getLogger(__name__)

NULL_VALUE = 'unspecified'


class BaseFilter(filters.FilterSet):
    def filter_with_multiple_query_values(self, queryset, name, value):
        options = set(value.split(','))
        null_lookup = {}
        if NULL_VALUE in options:
            options.remove(NULL_VALUE)
            null_lookup = {'__'.join([name, 'isnull']): True}
        lookup = {'__'.join([name, 'in']): options}
        return queryset.filter(Q(**lookup) | Q(**null_lookup))


class AssetFilter(BaseFilter):
    email = filters.CharFilter(
        field_name='assigned_to__user__email', lookup_expr='icontains'
    )
    model_number = filters.CharFilter(
        field_name='model_number__name',
        lookup_expr='iexact',
        method='filter_with_multiple_query_values',
    )
    asset_type = filters.CharFilter(
        field_name='model_number__asset_make__asset_type__name',
        lookup_expr='iexact',
        method='filter_with_multiple_query_values',
    )
    current_status = filters.CharFilter(
        field_name='current_status', lookup_expr='iexact'
    )
    verified = filters.CharFilter(field_name='verified', lookup_expr='iexact')

    class Meta:
        model = Asset
        fields = ['asset_type', 'model_number', 'email', 'current_status', 'verified']


class UserFilter(BaseFilter):
    cohort = filters.CharFilter(
        field_name='cohort',
        lookup_expr='iexact',
        method='filter_with_multiple_query_values',
    )

    email = filters.CharFilter(field_name='email', lookup_expr='istartswith')

    asset_count = filters.CharFilter(
        field_name='allocated_asset_count',
        label='Asset count',
        lookup_expr='iexact',
        method='filter_by_allocated_asset_count',
    )

    def filter_by_allocated_asset_count(self, queryset, name, value):
        users = [
            user.id
            for user in queryset
            if str(user.assetassignee.asset_set.count()) in value.split(',')
        ]
        return queryset.filter(id__in=users)

    class Meta:
        model = User
        fields = ['cohort', 'email', 'asset_count']
