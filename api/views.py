from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group
from django.core.validators import validate_email, ValidationError
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from itertools import chain
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from api.authentication import FirebaseTokenAuthentication
from core.models import Asset, SecurityUser, AssetLog, UserFeedback, \
    AssetStatus, AllocationHistory, AssetCategory, AssetSubCategory, \
    AssetType, AssetModelNumber, AssetCondition, AssetMake, \
    AssetIncidentReport, AssetSpecs, AssetAssignee
from core.models.officeblock import (
    OfficeBlock,
    OfficeFloor, OfficeWorkspace, OfficeFloorSection)
from core.models.department import Department
from .serializers import UserSerializer, \
    AssetSerializer, SecurityUserEmailsSerializer, \
    AssetLogSerializer, UserFeedbackSerializer, \
    AssetStatusSerializer, AllocationsSerializer, AssetCategorySerializer, \
    AssetSubCategorySerializer, AssetTypeSerializer, \
    AssetModelNumberSerializer, AssetConditionSerializer, \
    AssetMakeSerializer, AssetIncidentReportSerializer, \
    AssetHealthSerializer, SecurityUserSerializer, \
    AssetSpecsSerializer, OfficeBlockSerializer, \
    OfficeFloorSectionSerializer, OfficeFloorSerializer, UserGroupSerializer, \
    OfficeWorkspaceSerializer, DepartmentSerializer
from api.permissions import IsApiUser, IsSecurityUser

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class ManageAssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        queryset = Asset.objects.all()
        query_params = self.request.query_params

        if query_params.get('email'):
            email = query_params['email']
            try:
                validate_email(email)
                user_asset_assignee = User.objects.get(email=email)
                queryset = \
                    Asset.objects.filter(assigned_to__user=user_asset_assignee)
            except (ValidationError, ObjectDoesNotExist) as error:
                if error.__class__.__name__ == 'ValidationError':
                    raise serializers.ValidationError(error.message)
                queryset = Asset.objects.none()

        return queryset

    def get_object(self):
        queryset = Asset.objects.all()
        obj = get_object_or_404(queryset, uuid=self.kwargs['pk'])
        return obj

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
        except ValidationError as err:
            raise serializers.ValidationError(err.error_dict)
        return response


class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.query_params
        asset_assignee = AssetAssignee.objects.filter(user=user).first()
        queryset = Asset.objects.filter(assigned_to=asset_assignee)

        if query_params.get('email'):
            email = query_params['email']
            try:
                validate_email(email)
                user_asset_assignee = User.objects.get(email=email)
                queryset = \
                    Asset.objects.filter(assigned_to__user=user_asset_assignee)
            except (ValidationError, ObjectDoesNotExist) as error:
                if error.__class__.__name__ == 'ValidationError':
                    raise serializers.ValidationError(error.message)
                queryset = Asset.objects.none()

        return queryset

    def get_object(self):
        user = self.request.user
        asset_assignee = AssetAssignee.objects.filter(user=user).first()
        queryset = Asset.objects.filter(assigned_to=asset_assignee)
        obj = get_object_or_404(queryset, uuid=self.kwargs['pk'])
        return obj


class SecurityUserEmailsViewSet(ModelViewSet):
    serializer_class = SecurityUserEmailsSerializer
    http_method_names = ['get']
    permission_classes = (IsApiUser,)

    def list(self, request, *args, **kwargs):
        list_of_emails = [security_user.email
                          for security_user in SecurityUser.objects.all()]

        return Response({'emails': list_of_emails}, status=status.HTTP_200_OK)


class AssetLogViewSet(ModelViewSet):
    serializer_class = AssetLogSerializer
    queryset = AssetLog.objects.all()
    permission_classes = [IsSecurityUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user.securityuser)


class UserFeedbackViewSet(ModelViewSet):
    serializer_class = UserFeedbackSerializer
    queryset = UserFeedback.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class AssetStatusViewSet(ModelViewSet):
    serializer_class = AssetStatusSerializer
    queryset = AssetStatus.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']


class AllocationsViewSet(ModelViewSet):
    serializer_class = AllocationsSerializer
    queryset = AllocationHistory.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetCategoryViewSet(ModelViewSet):
    serializer_class = AssetCategorySerializer
    queryset = AssetCategory.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetSubCategoryViewSet(ModelViewSet):
    serializer_class = AssetSubCategorySerializer
    queryset = AssetSubCategory.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetTypeViewSet(ModelViewSet):
    serializer_class = AssetTypeSerializer
    queryset = AssetType.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetModelNumberViewSet(ModelViewSet):
    serializer_class = AssetModelNumberSerializer
    queryset = AssetModelNumber.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']


class AssetMakeViewSet(ModelViewSet):
    serializer_class = AssetMakeSerializer
    queryset = AssetMake.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']


class AssetConditionViewSet(ModelViewSet):
    serializer_class = AssetConditionSerializer
    queryset = AssetCondition.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = AssetIncidentReport.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class AssetHealthCountViewSet(ModelViewSet):
    serializer_class = AssetHealthSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', ]
    queryset = Asset.objects.all()
    data = None

    def _get_assets_status_condition(self, asset_models):
        asset_name, model_numbers = asset_models.popitem()

        def generate_asset_condition(model_number):
            statuses = {
                'Allocated': 0,
                'Available': 0,
                'Damaged': 0,
                'Lost': 0
            }

            def increment_asset_status(asset, model_number=model_number):
                if asset['asset_type'] == asset_name and \
                        asset['model_number'] == model_number:
                    nonlocal statuses
                    statuses[asset['count_by_status']] += 1
                return statuses

            list(map(increment_asset_status, self.data))
            return {
                'asset_type': asset_name,
                'model_number': model_number,
                'count_by_status': statuses
            }

        return list(map(generate_asset_condition, model_numbers))

    def _get_asset_list(self, asset):
        asset_with_status = list(map(self._get_assets_status_condition, asset))
        return list(chain.from_iterable(asset_with_status))

    def _get_asset_type(self, asset):
        return asset['asset_type']

    def _get_model_numbers(self, asset_type):
        asset_model_numbers = map(lambda asset: asset['model_number'], filter(
            lambda asset: asset['asset_type'] == asset_type, self.data))
        return {asset_type: set(list(asset_model_numbers))}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        is_admin = self.request.user.is_staff
        if is_admin:
            serializer = self.get_serializer(queryset, many=True)
            self.data = serializer.data
            asset_types = set(map(self._get_asset_type, self.data))
            asset = map(self._get_model_numbers, asset_types)
            asset_list = self._get_asset_list(asset)
            return Response(asset_list)
        return Response(exception=True, status=403,
                        data={'detail': ['You do not have authorization']})


class SecurityUserViewSet(ModelViewSet):
    serializer_class = SecurityUserSerializer
    queryset = SecurityUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']


class AssetSpecsViewSet(ModelViewSet):
    serializer_class = AssetSpecsSerializer
    queryset = AssetSpecs.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put']


class GroupViewSet(ModelViewSet):
    serializer_class = UserGroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        try:
            name = " ".join(serializer.validated_data.get(
                'name').title().split())
            serializer.save(name=name)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {"message": "{} already exist".format(name)})


class OfficeBlockViewSet(ModelViewSet):
    serializer_class = OfficeBlockSerializer
    queryset = OfficeBlock.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']


class OfficeFloorViewSet(ModelViewSet):
    serializer_class = OfficeFloorSerializer
    queryset = OfficeFloor.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']


class OfficeFloorSectionViewSet(ModelViewSet):
    serializer_class = OfficeFloorSectionSerializer
    queryset = OfficeFloorSection.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]


class OfficeWorkspaceViewSet(ModelViewSet):
    serializer_class = OfficeWorkspaceSerializer
    queryset = OfficeWorkspace.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)
