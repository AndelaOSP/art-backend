from rest_framework import serializers

from core.models import (
    User, Asset, SecurityUser, AssetLog,
    UserFeedback, CHECKIN, CHECKOUT, AssetStatus, AllocationHistory,
    AssetCategory, AssetSubCategory, AssetType, AssetModelNumber, AssetMake,
    AssetCondition
)


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
    assigned_to = UserSerializer(read_only=True)
    asset_type = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ("id", "asset_code", "serial_number", "model_number",
                  "checkin_status", "assigned_to", "created_at",
                  "last_modified", "current_status", 'asset_type'
                  )

    def get_checkin_status(self, obj):
        try:
            asset_log = AssetLog.objects.filter(asset=obj) \
                .order_by('-created_at').first()

            if asset_log.log_type == CHECKIN:
                return "checked_in"
            elif asset_log.log_type == CHECKOUT:
                return "checked_out"
        except AttributeError:
            return None

    def get_asset_type(self, obj):
        return obj.model_number.make_label.asset_type.asset_type


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


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ("reported_by", "message", "report_type", "created_at")
        read_only_fields = ("reported_by",)


class AssetStatusSerializer(AssetSerializer):
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = AssetStatus
        fields = ("id", "asset", "current_status", "status_history",
                  "previous_status", "created_at")

    def get_status_history(self, obj):
        asset_status = AssetStatus.objects.filter(asset=obj.asset)
        return [
            {
                "id": asset.id,
                "asset": asset.asset_id,
                "current_status": asset.current_status,
                "previous_status": asset.previous_status,
                "created_at": asset.created_at
            }
            for asset in asset_status if obj.created_at > asset.created_at
        ]


class AllocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocationHistory
        fields = ("asset", "current_owner", "previous_owner", "created_at")
        read_only_fields = ("previous_owner",)


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ("id", "category_name", "created_at", "last_modified")


class AssetSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSubCategory
        fields = ("id", "sub_category_name", "asset_category",
                  "created_at", "last_modified")


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ("id", "asset_type", "asset_sub_category",
                  "created_at", "last_modified")


class AssetModelNumberSerializer(serializers.ModelSerializer):
    make_label = serializers.SerializerMethodField()

    class Meta:
        model = AssetModelNumber
        fields = ('id', 'model_number', 'make_label',
                  'created_at', 'last_modified')

    def get_make_label(self, obj):
        return obj.make_label.make_label

    def to_internal_value(self, data):
        make_label = data.get('make_label')
        if not make_label:
            raise serializers.ValidationError({
                'make_label': [self.error_messages['required']]
            })
        try:
            make_label_instance = AssetMake.objects.get(
                id=make_label)
        except Exception:
            raise serializers.ValidationError({
                'make_label': [
                    f'Invalid pk \"{make_label}\" - object does not exist.'
                ]})

        internal_value = super().to_internal_value(data)
        internal_value.update({
            'make_label': make_label_instance
        })
        return internal_value


class AssetConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCondition
        fields = ("id", "asset", "asset_condition",
                  "created_at")
