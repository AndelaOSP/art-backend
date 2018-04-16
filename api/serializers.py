from rest_framework import serializers

from .models import User, Item, SecurityUser, AssetLog


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'email', 'cohort',
            'slack_handle', 'picture', 'phone_number',
            'last_modified', 'date_joined', 'last_login'
        )

        extra_kwargs = {
            'last_modified': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
            'cohort': {'min_value': 0}
        }

    def get_full_name(self, obj):
        return "{} {}".format(
            obj.first_name,
            obj.last_name
        )

    def create(self, validated_data):
        user = User(**validated_data)
        user.save()
        return user


class AssetSerializer(serializers.ModelSerializer):
    checkin_status = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ("id", "item_code", "serial_number", "model_number",
                  "allocation_status", "checkin_status", "assigned_to",
                  "created_at", "last_modified",
                  )

    def get_checkin_status(self, obj):
        try:
            asset_log = AssetLog.objects.get(asset=obj)
            return asset_log.log_type
        except AssetLog.DoesNotExist:
            return None


class SecurityUserEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityUser
        fields = ("email",)


class AssetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLog
        fields = (
            "id", "asset", "log_type",
            "created_at", "last_modified",
        )


class AssetDetailSerializer(AssetSerializer):
    assigned_to = UserSerializer(read_only=True)
