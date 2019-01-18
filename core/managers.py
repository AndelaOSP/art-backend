# Third-Party Imports
from django.db.models import Manager
from django.db.models.query import QuerySet


class CaseInsensitiveQuerySet(QuerySet):
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        fields = [
            'category_name',
            'sub_category_name',
            'asset_type',
            'make_label',
            'model_number',
            'asset_code',
            'serial_number',
        ]
        for field in fields:
            if field in kwargs and type(kwargs.get(field)) == str:
                kwargs['{}__iexact'.format(field)] = kwargs[field]
                del kwargs[field]
        return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(
            mapper, *args, **kwargs
        )


class CaseInsensitiveManager(Manager):
    def get_queryset(self):
        return CaseInsensitiveQuerySet(self.model)
