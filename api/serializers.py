from rest_framework import serializers
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from core.models import (
    User, Asset, SecurityUser, AssetLog,
    UserFeedback, CHECKIN, CHECKOUT, AssetStatus, AllocationHistory,
    AssetCategory, AssetSubCategory, AssetType, AssetModelNumber, AssetMake,
    AssetAssignee, AssetCondition, AssetIncidentReport, AssetSpecs,
    OfficeBlock, OfficeFloor, OfficeFloorSection, OfficeWorkspace
)
from core.models.department import Department


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    allocated_asset_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'email', 'cohort',
            'slack_handle', 'picture', 'phone_number',
            'allocated_asset_count', 'last_modified', 'date_joined',
            'last_login'
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

    def get_allocated_asset_count(self, obj):
        """Return the number of assets allocated to a user.

        obj is an instance of the User when /api/v1/users is loaded and
        an instance of the AssetAssignee when /api/v1/manage-assets is loaded

        """
        try:
            return obj.assetassignee.current_owner_asset.count()
        except AttributeError:
            if isinstance(obj, User):
                # In the unlikely event that a User has no corresponding
                # AssetAssignee instance create it by calling save()
                obj.save()
            elif isinstance(obj, AssetAssignee):
                return obj.current_owner_asset.count()
            else:
                return 0

    def create(self, validated_data):
        user = User(**validated_data)
        user.save()
        return user


class UserSerializerWithAssets(UserSerializer):
    allocated_assets = serializers.SerializerMethodField()

    def get_allocated_assets(self, obj):
        assets = Asset.objects.filter(assigned_to__user=obj)
        serialized_assets = AssetSerializer(assets, many=True)
        return serialized_assets.data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('allocated_assets',)


class AssetSerializer(serializers.ModelSerializer):
    checkin_status = serializers.SerializerMethodField()
    allocation_history = serializers.SerializerMethodField()
    assigned_to = UserSerializer(read_only=True)
    asset_category = serializers.SerializerMethodField()
    asset_sub_category = serializers.SerializerMethodField()
    make_label = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    model_number = serializers.SlugRelatedField(
        queryset=AssetModelNumber.objects.all(),
        slug_field="model_number"
    )

    class Meta:
        model = Asset
        fields = ('id', 'uuid', 'asset_category', 'asset_sub_category', 'make_label',
                  'asset_code', 'serial_number', 'model_number',
                  'checkin_status', 'created_at',
                  'last_modified', 'current_status', 'asset_type',
                  'allocation_history', 'specs', 'purchase_date',
                  'notes', 'assigned_to',
                  )
        depth = 1
        read_only_fields = ("uuid",)

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

    def get_asset_category(self, obj):
        return obj.model_number.make_label.asset_type. \
            asset_sub_category.asset_category.category_name

    def get_asset_sub_category(self, obj):
        return obj.model_number.make_label.asset_type. \
            asset_sub_category.sub_category_name

    def get_make_label(self, obj):
        return obj.model_number.make_label.make_label

    def get_asset_type(self, obj):
        return obj.model_number.make_label.asset_type.asset_type

    def get_allocation_history(self, obj):
        allocations = AllocationHistory.objects.filter(asset=obj.id)
        return [
            {
                "id": allocation.id,
                "current_owner": allocation.current_owner.email
                if allocation.current_owner else None,
                "previous_owner": allocation.previous_owner.email
                if allocation.previous_owner else None,
                "created_at": allocation.created_at
            }
            for allocation in allocations
        ]

    def to_internal_value(self, data):
        internals = super(AssetSerializer, self).to_internal_value(data)
        specs_serializer = AssetSpecsSerializer(data=data)
        specs_serializer.is_valid()

        if len(specs_serializer.data):
            try:
                specs, _ = AssetSpecs.objects.get_or_create(
                    **specs_serializer.data
                )
            except ValidationError as err:
                raise serializers.ValidationError(err.error_dict)
            internals['specs'] = specs
        return internals


class AssetAssigneeSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = AssetAssignee
        fields = ("id", "assignee",)

    def get_assignee(self, obj):
        if obj.user:
            return obj.user.email

        elif obj.department:
            return obj.department.name

        elif obj.workspace:
            return obj.workspace.name


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

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code
        instance_data['checked_by'] = instance.checked_by.email
        instance_data['asset'] = f"{serial_no} - {asset_code}"
        return instance_data


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ("reported_by", "message", "report_type", "created_at")
        read_only_fields = ("reported_by",)

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        user = User.objects.get(id=instance.reported_by.id)
        instance_data['reported_by'] = user.email
        return instance_data


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

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code
        instance_data['asset'] = f"{asset_code} - {serial_no}"
        return instance_data


class AllocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocationHistory
        fields = ("asset", "current_owner", "previous_owner", "created_at")
        read_only_fields = ("previous_owner",)

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code

        if instance.previous_owner:
            instance_data['previous_owner'] = instance.previous_owner.email
        if instance.current_owner:
            instance_data['current_owner'] = instance.current_owner.email
        instance_data['asset'] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ("id", "category_name", "created_at", "last_modified")


class AssetSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSubCategory
        fields = ("id", "sub_category_name", "asset_category",
                  "created_at", "last_modified")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data['asset_category'] = AssetCategory.objects.get(
            id=instance.asset_category.id).category_name
        return instance_data


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ("id", "asset_type", "asset_sub_category",
                  "created_at", "last_modified")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data['asset_sub_category'] = AssetSubCategory.objects.get(
            id=instance.asset_sub_category.id
        ).sub_category_name
        return instance_data


class AssetModelNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetModelNumber
        fields = ('id', 'model_number', 'make_label',
                  'created_at', 'last_modified')

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        instance_data['make_label'] = AssetMake.objects.get(
            id=instance.make_label.id).make_label
        return instance_data

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
        fields = ("id", "asset", "notes",
                  "created_at")

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code
        instance_data['asset'] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetMakeSerializer(serializers.ModelSerializer):
    asset_type = serializers.SerializerMethodField()

    class Meta:
        model = AssetMake
        fields = ('id', 'make_label', 'asset_type',
                  'created_at', 'last_modified_at')

    def get_asset_type(self, obj):
        return obj.asset_type.asset_type

    def to_internal_value(self, data):
        asset_type = data['asset_type']
        if not asset_type:
            raise serializers.ValidationError({'asset_type': [
                self.error_messages['required']]})
        try:
            asset_type_instance = AssetType.objects.get(id=asset_type)
        except Exception:
            raise serializers.ValidationError({'asset_type': [
                f'Invalid pk \"{asset_type}\" - object does not exist.']})
        internal_value = super().to_internal_value(data)
        internal_value.update({'asset_type': asset_type_instance})
        return internal_value


class AssetIncidentReportSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SerializerMethodField()

    class Meta:
        model = AssetIncidentReport
        fields = ('id', 'asset', 'incident_type', 'incident_location',
                  'incident_description', 'injuries_sustained',
                  'loss_of_property', 'witnesses',
                  'submitted_by', 'police_abstract_obtained')

    def get_submitted_by(self, instance):
        if instance.submitted_by:
            return instance.submitted_by.email
        return instance.submitted_by

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        asset = Asset.objects.get(id=instance.asset.id)
        serial_no = asset.serial_number
        asset_code = asset.asset_code
        instance_data['asset'] = f"{serial_no} - {asset_code}"
        return instance_data


class AssetHealthSerializer(serializers.ModelSerializer):
    asset_type = serializers.SerializerMethodField()
    model_number = serializers.SerializerMethodField()
    count_by_status = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ('asset_type', 'model_number', 'count_by_status',)

    def get_asset_type(self, obj):
        return obj.model_number.make_label.asset_type.asset_type

    def get_count_by_status(self, obj):
        return obj.current_status

    def get_model_number(self, obj):
        return obj.model_number.model_number


class SecurityUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityUser
        fields = (
            'id', 'first_name', 'last_name', 'email',
            'badge_number', 'phone_number', 'last_modified',
            'date_joined', 'last_login'
        )

        extra_kwargs = {
            'last_modified': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True}
        }


class AssetSpecsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSpecs
        fields = (
            'id', 'year_of_manufacture', 'processor_speed', 'screen_size',
            'processor_type', 'storage', 'memory'
        )
        extra_kwargs = {
            'processor_speed': {'required': False},
            'processor_type': {'required': False},
            'screen_size': {'required': False},
            'memory': {'required': False},
            'storage': {'required': False},
            'year_of_manufacture': {'required': False}
        }
        validators = []

    def validate(self, fields):
        not_unique = AssetSpecs.objects.filter(**fields).exists()
        if not_unique:
            raise serializers.ValidationError(
                "Similar asset specification already exist"
            )
        return fields


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class OfficeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeBlock
        fields = ("name", "id",)


class OfficeFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeFloor
        fields = ("number", "block", "id")


class OfficeFloorSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeFloorSection
        fields = ("name", "floor", "id")


class OfficeWorkspaceSerializer(serializers.ModelSerializer):
    floor = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()

    class Meta:
        model = OfficeWorkspace
        fields = ("id", "name", "section", "floor", "block")

    def get_floor(self, obj):
        return obj.section.floor.number

    def get_block(self, obj):
        return obj.section.floor.block.name


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("name", "id",)
