# Third-Party Imports
from rest_framework import serializers

# App Imports
from core import models


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.History
        fields = ("id", "table_name", "item_id", "action", "user", "body", "created_at")
