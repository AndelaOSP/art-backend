from django_filters import rest_framework as filters

from core.models import Asset, User


class AssetFilter(filters.FilterSet):
    email = filters.CharFilter(
        field_name='assigned_to__user__email',
        lookup_expr='icontains', )
    model_number = filters.CharFilter(
        field_name='model_number__model_number',
        lookup_expr='iexact',
        method='filter_with_multiple_query_values')
    asset_type = filters.CharFilter(
        field_name='model_number__make_label__asset_type__asset_type',
        lookup_expr='iexact',
        method='filter_with_multiple_query_values')
    current_status = filters.CharFilter(
        field_name='current_status',
        lookup_expr='iexact',
    )

    def filter_with_multiple_query_values(self, queryset, name, value):
        lookup = '__'.join([name, 'in'])
        return queryset.filter(**{lookup: value.split(',')})

    class Meta:
        model = Asset
        fields = ['asset_type', 'model_number', 'email', 'current_status']


class UserFilter(filters.FilterSet):
    cohort = filters.CharFilter(
        field_name='cohort',
        lookup_expr='iexact',)

    email = filters.CharFilter(
        field_name='email',
        lookup_expr='istartswith',)

    asset_count = filters.CharFilter(
        field_name='allocated_asset_count',
        label='Asset count',
        lookup_expr='iexact',
        method='filter_by_allocated_asset_count',)

    def filter_by_allocated_asset_count(self, queryset, name, value):
        users = [
            user.id
            for user in queryset
            if user.assetassignee.asset_set.count() == int(value)
        ]
        return User.objects.filter(id__in=users)

    class Meta:
        model = User
        fields = ['cohort', 'email', 'asset_count']
