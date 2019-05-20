# Third-Party Imports
from django.contrib.auth.models import Group
from rest_framework import serializers

# App Imports
from core import models


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    allocated_asset_count = serializers.SerializerMethodField()
    department = serializers.SlugRelatedField(
        read_only=False,
        slug_field="name",
        queryset=models.Department.objects.all(),
        required=False,
    )

    class Meta:
        model = models.User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_staff",
            "cohort",
            "slack_id",
            "picture",
            "phone_number",
            "location",
            "allocated_asset_count",
            "last_modified",
            "date_joined",
            "last_login",
            "department",
        )

        extra_kwargs = {
            "last_modified": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "cohort": {"min_value": 0},
        }

    def get_full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

    def get_allocated_asset_count(self, obj):
        """Return the number of assets allocated to a user.

        obj is an instance of the User when /api/v1/users is loaded and
        an instance of the AssetAssignee when /api/v1/manage-assets is loaded

        """
        try:
            return obj.assetassignee.asset_set.count()
        except AttributeError:
            if isinstance(obj, models.User):
                # In the unlikely event that a User has no corresponding
                # AssetAssignee instance create it by calling save()
                obj.save()
            elif isinstance(obj, models.AssetAssignee):
                return obj.asset_set.count()
            else:
                return 0

    def create(self, validated_data):
        user = models.User(**validated_data)
        user.save()
        return user


class UserSerializerWithAssets(UserSerializer):
    allocated_assets = serializers.SerializerMethodField()

    def get_allocated_assets(self, obj):
        from .assets import AssetSerializer

        assets = models.Asset.objects.filter(assigned_to__user=obj)
        serialized_assets = AssetSerializer(assets, many=True)
        return serialized_assets.data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("allocated_assets",)


class SecurityUserEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("email",)


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFeedback
        fields = ("reported_by", "message", "report_type", "created_at", "resolved")
        read_only_fields = ("reported_by", "resolved")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data["reported_by"] = instance.reported_by.email
        return instance_data


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)
