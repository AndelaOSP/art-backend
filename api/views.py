from django.contrib.auth import get_user_model
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
    AssetIncidentReport
from .serializers import UserSerializer, \
    AssetSerializer, SecurityUserEmailsSerializer, \
    AssetLogSerializer, UserFeedbackSerializer, \
    AssetStatusSerializer, AllocationsSerializer, AssetCategorySerializer, \
    AssetSubCategorySerializer, AssetTypeSerializer, \
    AssetModelNumberSerializer, AssetConditionSerializer, \
    AssetMakeSerializer, AssetIncidentReportSerializer, \
    AssetHealthSerializer, SecurityUserSerializer
from api.permissions import IsApiUser, IsSecurityUser

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        is_admin = self.request.user.is_staff
        queryset = Asset.objects.all()
        query_params = self.request.query_params

        if not is_admin:
            queryset = Asset.objects.filter(assigned_to=user)

        if query_params.get('email'):
            email = query_params['email']
            try:
                validate_email(email)
            except ValidationError as error:
                raise serializers.ValidationError(error.message)
            queryset = Asset.objects.filter(assigned_to__email=email)

        return queryset

    def get_object(self):
        queryset = Asset.objects.all()
        obj = get_object_or_404(queryset, serial_number=self.kwargs['pk'])
        return obj

    def perform_create(self, serializer):
        serializer.save()


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


    def get_queryset(self):
          
        if 'pk' in self.kwargs:
            return AllocationHistory.objects.filter(asset=self.kwargs['pk'])
        return AllocationHistory.objects.all()

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


class AssetHealthCountViewSet(ModelViewSet):
    serializer_class = AssetHealthSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication, )
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
