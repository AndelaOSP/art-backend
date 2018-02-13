from rest_framework import routers, serializers, viewsets
from api.models import Asset, CheckinLogs, CheckoutLogs

# Serializers define the API representation.


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Asset
        fields = ('full_name', 'cohort', 'mac_book_sn', 'mac_book_tag',
                  'charger_tag', 'tb_dongle_tag', 'headsets_sn', 'headsets_tag',
                  'date_created', 'date_modified')
        read_only_fields = ('date_created', 'date_modified')


class CheckinLogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CheckinLogs
        fields = ('user_id', 'mac_book', 'charger', 'tb_dongle', 'head_set',
                  'date_created')
        read_only_fields = ('date_created', 'time_created', 'app_time_stamp')


class CheckoutLogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CheckoutLogs
        fields = ('user_id', 'mac_book', 'charger', 'tb_dongle', 'head_set',
                  'date_created')
        read_only_fields = ('date_created', 'time_created', 'app_time_stamp')
