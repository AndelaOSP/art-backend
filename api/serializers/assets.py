# Third-Party Imports
from django.core.exceptions import ValidationError
from rest_framework import serializers

# App Imports
from core import models
from core.constants import CHECKIN, CHECKOUT


class AssetSerializer(serializers.ModelSerializer):
    checkin_status = serializers.SerializerMethodField()
    allocation_history = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    asset_category = serializers.ReadOnlyField()
    asset_sub_category = serializers.ReadOnlyField()
    asset_make = serializers.ReadOnlyField()
    make_label = serializers.ReadOnlyField(source="asset_make")
    asset_type = serializers.ReadOnlyField()
    asset_location = serializers.SlugRelatedField(
        many=False,
        slug_field="name",
        required=False,
        queryset=models.AndelaCentre.objects.all(),
    )
    department = serializers.SlugRelatedField(
        read_only=False,
        slug_field="name",
        queryset=models.Department.objects.all(),
        required=False,
    )

    model_number = serializers.SlugRelatedField(
        queryset=models.AssetModelNumber.objects.all(), slug_field="name"
    )

    class Meta:
        model = models.Asset
        fields = (
            "id",
            "uuid",
            "asset_category",
            "asset_sub_category",
            "asset_make",
            "make_label",
            "asset_code",
            "serial_number",
            "model_number",
            "checkin_status",
            "created_at",
            "last_modified",
            "current_status",
            "asset_type",
            "allocation_history",
            "specs",
            "purchase_date",
            "notes",
            "assigned_to",
            "asset_location",
            "verified",
            "invoice_receipt",
            "department",
            "active",
            "paid_or_postpaid",
        )
        depth = 1
        read_only_fields = (
            "uuid",
            "created_at",
            "last_modified",
            "assigned_to",
            "current_status",
            "notes",
            "asset_category",
            "asset_sub_category",
            "asset_make",
        )

    def get_checkin_status(self, obj):
        try:
            asset_log = (
                models.AssetLog.objects.filter(asset=obj)
                .order_by("-created_at")
                .first()
            )
            if asset_log.log_type == CHECKIN:
                return "checked_in"
            elif asset_log.log_type == CHECKOUT:
                return "checked_out"
        except AttributeError:
            return None

    def get_assigned_to(self, obj):
        if not obj.assigned_to:
            return None
        if obj.assigned_to.department:
            from api.serializers import DepartmentSerializer

            serialized_data = DepartmentSerializer(obj.assigned_to.department)
        elif obj.assigned_to.workspace:
            from api.serializers import OfficeWorkspaceSerializer

            serialized_data = OfficeWorkspaceSerializer(obj.assigned_to.workspace)
        elif obj.assigned_to.user:
            from api.serializers import UserSerializer

            serialized_data = UserSerializer(obj.assigned_to.user)
        else:
            return None
        return serialized_data.data

    def get_allocation_history(self, obj):
        allocations = models.AllocationHistory.objects.filter(asset=obj.id)
        return [
            {
                "id": allocation.id,
                "current_owner": allocation.current_owner.email
                if allocation.current_owner
                else None,
                "previous_owner": allocation.previous_owner.email
                if allocation.previous_owner
                else None,
                "assigner": allocation.assigner.email if allocation.assigner else None,
                "created_at": allocation.created_at,
            }
            for allocation in allocations
        ]

    def to_internal_value(self, data):
        internals = super(AssetSerializer, self).to_internal_value(data)
        specs_serializer = AssetSpecsSerializer(data=data)
        specs_serializer.is_valid()
        if len(specs_serializer.data):
            try:
                specs, _ = models.AssetSpecs.objects.get_or_create(
                    **specs_serializer.data
                )
            except ValidationError as err:
                raise serializers.ValidationError(err.error_dict)
            internals["specs"] = specs
        return internals


class AssetAssigneeSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = models.AssetAssignee
        fields = ("id", "assignee")

    def get_assignee(self, obj):
        if obj.user:
            return obj.user.email

        elif obj.department:
            return obj.department.name

        elif obj.workspace:
            return obj.workspace.name


class AssetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetLog
        fields = ("id", "asset", "log_type", "created_at", "last_modified")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = models.Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code
        instance_data["checked_by"] = instance.checked_by.email
        instance_data["asset"] = f"{serial_no} - {asset_code}"
        return instance_data

    def validate(self, fields):
        existing_log = models.AssetLog.objects.filter(asset=fields["asset"])
        existing_log = existing_log.first()
        if existing_log and existing_log.log_type == fields["log_type"]:
            raise serializers.ValidationError(
                f"The asset log type is already {existing_log.log_type}"
            )
        return fields


class AssetStatusSerializer(AssetSerializer):
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = models.AssetStatus
        fields = (
            "id",
            "asset",
            "current_status",
            "status_history",
            "previous_status",
            "created_at",
        )

    def get_status_history(self, obj):
        asset_status = models.AssetStatus.objects.filter(asset=obj.asset)
        return [
            {
                "id": asset.id,
                "asset": asset.asset_id,
                "current_status": asset.current_status,
                "previous_status": asset.previous_status,
                "created_at": asset.created_at,
            }
            for asset in asset_status
            if obj.created_at > asset.created_at
        ]

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        serial_no = instance.asset.serial_number
        asset_code = instance.asset.asset_code
        instance_data["asset"] = f"{asset_code} - {serial_no}"
        return instance_data


class AllocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllocationHistory
        fields = ("asset", "current_owner", "previous_owner", "assigner", "created_at")
        read_only_fields = ("previous_owner",)

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        serial_no = instance.asset.serial_number
        asset_code = instance.asset.asset_code

        if instance.previous_owner:
            instance_data["previous_owner"] = instance.previous_owner.email
        if instance.current_owner:
            instance_data["current_owner"] = instance.current_owner.email
        if instance.assigner:
            instance_data["assigner"] = instance.assigner.email

        instance_data["asset"] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="name")

    class Meta:
        model = models.AssetCategory
        fields = ("id", "name", "created_at", "last_modified", "category_name")

    def to_internal_value(self, data):
        _data = data.copy()
        if not _data.get("name"):
            _data["name"] = _data.get("category_name")
        internal_value = super().to_internal_value(_data)
        return internal_value


class AssetSubCategorySerializer(serializers.ModelSerializer):
    sub_category_name = serializers.ReadOnlyField(source="name")

    class Meta:
        model = models.AssetSubCategory
        fields = (
            "id",
            "name",
            "asset_category",
            "created_at",
            "last_modified",
            "sub_category_name",
        )

    def to_internal_value(self, data):
        _data = data.copy()
        if not _data.get("name"):
            _data["name"] = _data.get("sub_category_name")
        internal_value = super().to_internal_value(_data)
        return internal_value

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data["asset_category"] = instance.asset_category.name
        return instance_data


class AssetTypeSerializer(serializers.ModelSerializer):
    asset_type = serializers.ReadOnlyField(source="name")

    class Meta:
        model = models.AssetType
        fields = (
            "id",
            "name",
            "asset_sub_category",
            "has_specs",
            "created_at",
            "last_modified",
            "asset_type",
        )

    def to_internal_value(self, data):
        _data = data.copy()
        if not data.get("name"):
            _data["name"] = _data.get("asset_type")
        internal_value = super().to_internal_value(_data)
        return internal_value

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data["asset_sub_category"] = instance.asset_sub_category.name
        return instance_data


class AssetModelNumberSerializer(serializers.ModelSerializer):
    make_label = serializers.SerializerMethodField()
    model_number = serializers.ReadOnlyField(source="name")

    class Meta:
        model = models.AssetModelNumber
        fields = (
            "id",
            "name",
            "asset_make",
            "created_at",
            "last_modified",
            "model_number",
            "make_label",
        )

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data["asset_make"] = instance.asset_make.name
        return instance_data

    def to_internal_value(self, data):
        _data = data.copy()
        if not _data.get("asset_make"):
            _data["asset_make"] = _data.get("make_label")
        if not _data.get("name"):
            _data["name"] = _data.get("model_number")
        asset_make = _data.get("asset_make")
        if not asset_make:
            raise serializers.ValidationError(
                {"asset_make": [self.error_messages["required"]]}
            )
        try:
            asset_make_instance = models.AssetMake.objects.get(id=asset_make)
        except Exception:
            raise serializers.ValidationError(
                {"asset_make": [f'Invalid pk "{asset_make}" - object does not exist.']}
            )
        internal_value = super().to_internal_value(_data)
        internal_value.update({"asset_make": asset_make_instance})
        return internal_value

    def get_make_label(self, obj):
        return obj.asset_make.name


class AssetConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetCondition
        fields = ("id", "asset", "notes", "created_at")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        serial_no = instance.asset.serial_number
        asset_code = instance.asset.asset_code
        instance_data["asset"] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetMakeSerializer(serializers.ModelSerializer):
    asset_type = serializers.SerializerMethodField()
    make_label = serializers.SerializerMethodField()

    class Meta:
        model = models.AssetMake
        fields = (
            "id",
            "name",
            "asset_type",
            "created_at",
            "last_modified_at",
            "make_label",
        )

    def get_asset_type(self, obj):
        return obj.asset_type.name

    def get_make_label(self, obj):
        return obj.name

    def to_internal_value(self, data):
        _data = data.copy()
        if not _data.get("name"):
            _data["name"] = _data.get("make_label")
        asset_type = _data["asset_type"]
        if not asset_type:
            raise serializers.ValidationError(
                {"asset_type": [self.error_messages["required"]]}
            )
        try:
            asset_type_instance = models.AssetType.objects.get(id=asset_type)
        except Exception:
            raise serializers.ValidationError(
                {"asset_type": [f'Invalid pk "{asset_type}" - object does not exist.']}
            )
        internal_value = super().to_internal_value(_data)
        internal_value.update({"asset_type": asset_type_instance})
        return internal_value


class AssetIncidentReportSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SerializerMethodField()

    class Meta:
        model = models.AssetIncidentReport
        fields = (
            "id",
            "asset",
            "incident_type",
            "incident_location",
            "incident_description",
            "injuries_sustained",
            "loss_of_property",
            "witnesses",
            "submitted_by",
            "police_abstract_obtained",
        )

    def get_submitted_by(self, instance):
        if instance.submitted_by:
            return instance.submitted_by.email
        return instance.submitted_by

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        serial_no = instance.asset.serial_number
        asset_code = instance.asset.asset_code
        instance_data["asset"] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetHealthSerializer(serializers.ModelSerializer):
    asset_type = serializers.ReadOnlyField()
    model_number = serializers.ReadOnlyField(source="model_number__name")
    count_by_status = serializers.ReadOnlyField(source="current_status")

    class Meta:
        model = models.Asset
        fields = ("asset_type", "model_number", "count_by_status")


class DepartmentAssetSerializer(serializers.ModelSerializer):
    asset_type = serializers.ReadOnlyField()

    class Meta:
        model = models.Asset
        fields = ("uuid", "asset_category", "serial_number", "asset_code", "asset_type")


class AssetSpecsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetSpecs
        fields = (
            "id",
            "year_of_manufacture",
            "processor_speed",
            "screen_size",
            "processor_type",
            "storage",
            "memory",
        )
        extra_kwargs = {
            "processor_speed": {"required": False},
            "processor_type": {"required": False},
            "screen_size": {"required": False},
            "memory": {"required": False},
            "storage": {"required": False},
            "year_of_manufacture": {"required": False},
        }
        validators = []

    def validate(self, fields):
        not_unique = models.AssetSpecs.objects.filter(**fields).exists()
        if not_unique:
            raise serializers.ValidationError(
                "Similar asset specification already exist"
            )
        return fields


class StateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StateTransition
        fields = (
            "id",
            "asset_incident_report",
            "incident_report_state",
            "asset_state_from_report",
        )
