from django_filters import rest_framework as filters

from core.models import Asset


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

    def filter_with_multiple_query_values(self, queryset, name, value):
        lookup = '__'.join([name, 'in'])
        return queryset.filter(**{lookup: value.split(',')})

    class Meta:
        model = Asset
        fields = ['asset_type', 'model_number', 'email']
