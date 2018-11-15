import csv
import codecs
import os
import re
from itertools import chain

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group
from django.core.validators import ValidationError
from django.http import FileResponse
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from api.authentication import FirebaseTokenAuthentication
from api.filters import AssetFilter, UserFilter
from core.assets_saver_helper import save_asset
from core.models import Asset, SecurityUser, AssetLog, UserFeedback, \
    AssetStatus, AllocationHistory, AssetCategory, AssetSubCategory, \
    AssetType, AssetModelNumber, AssetCondition, AssetMake, \
    AssetIncidentReport, AssetSpecs, AssetAssignee, AndelaCentre
from core.models.officeblock import (
    OfficeBlock,
    OfficeFloor, OfficeWorkspace, OfficeFloorSection)
from core.models.department import Department
from core.slack_bot import SlackIntegration
from .serializers import UserSerializerWithAssets, \
    AssetSerializer, SecurityUserEmailsSerializer, \
    AssetLogSerializer, UserFeedbackSerializer, \
    AssetStatusSerializer, AllocationsSerializer, AssetCategorySerializer, \
    AssetSubCategorySerializer, AssetTypeSerializer, \
    AssetModelNumberSerializer, AssetConditionSerializer, \
    AssetMakeSerializer, AssetIncidentReportSerializer, \
    AssetHealthSerializer, SecurityUserSerializer, \
    AssetSpecsSerializer, OfficeBlockSerializer, \
    OfficeFloorSectionSerializer, OfficeFloorSerializer, UserGroupSerializer, \
    OfficeWorkspaceSerializer, DepartmentSerializer, \
    AssetAssigneeSerializer, AndelaCentreSerializer
from api.permissions import IsApiUser, IsSecurityUser

User = get_user_model()
slack = SlackIntegration()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializerWithAssets
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter


class ManageAssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssetFilter

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = Asset.objects.filter(asset_location=user_location)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, uuid=self.kwargs['pk'])
        return obj

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
        except ValidationError as err:
            raise serializers.ValidationError(err.error_dict)
        return response

    def perform_create(self, serializer):
        serializer.save(asset_location=self.request.user.location)


class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        asset_assignee = AssetAssignee.objects.filter(user=user).first()
        queryset = Asset.objects.filter(
            assigned_to=asset_assignee,
            asset_location=user.location)

        return queryset

    def get_object(self):
        user = self.request.user
        user_location = self.request.user.location
        asset_assignee = AssetAssignee.objects.filter(user=user).first()
        queryset = Asset.objects.filter(
            assigned_to=asset_assignee, asset_location=user_location)
        obj = get_object_or_404(queryset, uuid=self.kwargs['pk'])
        return obj


class AssetAssigneeViewSet(ModelViewSet):
    serializer_class = AssetAssigneeSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = AssetAssignee.objects.filter(user__location=user_location)
        return queryset


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
    permission_classes = [IsSecurityUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = AssetLog.objects.filter(asset__asset_location=user_location)
        return queryset

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
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = AssetStatus.objects.filter(
            asset__asset_location=user_location)
        return queryset


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
    filter_backends = (OrderingFilter,)
    ordering = ('category_name',)
    http_method_names = ['get', 'post']


class AssetSubCategoryViewSet(ModelViewSet):
    serializer_class = AssetSubCategorySerializer
    queryset = AssetSubCategory.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ('sub_category_name',)
    http_method_names = ['get', 'post']


class AssetTypeViewSet(ModelViewSet):
    serializer_class = AssetTypeSerializer
    queryset = AssetType.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ('asset_type',)
    http_method_names = ['get', 'post']


class AssetModelNumberViewSet(ModelViewSet):
    serializer_class = AssetModelNumberSerializer
    queryset = AssetModelNumber.objects.all()
    permission_classes = [IsAuthenticated, ]
    filter_backends = (OrderingFilter,)
    ordering = ('model_number',)
    http_method_names = ['get', 'post']


class AssetMakeViewSet(ModelViewSet):
    serializer_class = AssetMakeSerializer
    queryset = AssetMake.objects.all()
    permission_classes = [IsAuthenticated, ]
    filter_backends = (OrderingFilter,)
    ordering = ('make_label',)
    http_method_names = ['get', 'post']


class AssetConditionViewSet(ModelViewSet):
    serializer_class = AssetConditionSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = AssetCondition.objects.filter(
            asset__asset_location=user_location)
        return queryset


class AssetIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = AssetIncidentReport.objects.filter(
            asset__asset_location=user_location)
        return queryset

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class AssetSlackIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = AssetIncidentReport.objects.all()
    http_method_names = ['post']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    def create(self, request, *args, **kwargs):
        if (
            self.request.data.get('command', None) is None) and \
                (self.request.data.get('payload', None) is None):
            try:
                response = super().create(request, *args, **kwargs)
            except ValidationError as err:
                raise serializers.ValidationError(err.error_dict)
            return response
        else:
            bot = slack.send_incidence_report(
                self.request.data, Asset, AssetIncidentReport, User)
            if bot:
                return Response(status=status.HTTP_200_OK)


class AssetHealthCountViewSet(ModelViewSet):
    serializer_class = AssetHealthSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', ]
    data = None

    def get_queryset(self):
        user_location = self.request.user.location
        queryset = Asset.objects.filter(asset_location=user_location)
        return queryset

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
        except IntegrityError:
            raise serializers.ValidationError(
                {"message": "{} already exist".format(name)})


class OfficeBlockViewSet(ModelViewSet):
    serializer_class = OfficeBlockSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        return OfficeBlock.objects.filter(location=user_location)


class OfficeFloorViewSet(ModelViewSet):
    serializer_class = OfficeFloorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        return OfficeFloor.objects.filter(block__location=user_location)


class OfficeFloorSectionViewSet(ModelViewSet):
    serializer_class = OfficeFloorSectionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def get_queryset(self):
        user_location = self.request.user.location
        return OfficeFloorSection.objects.filter(
            floor__block__location=user_location)


class OfficeWorkspaceViewSet(ModelViewSet):
    serializer_class = OfficeWorkspaceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        user_location = self.request.user.location
        return OfficeWorkspace.objects.filter(
            section__floor__block__location=user_location)

    def get_object(self):
        user_location = self.request.user.location
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'])
        return obj

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


class AssetsImportViewSet(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):  # noqa
        file_obj = request.data.get('file')
        if not file_obj:
            # file_obj is none so return error
            return Response(
                {"error": "Csv file to import from not provided"}, status=400)

        file_obj = codecs.iterdecode(file_obj, 'utf-8')
        csv_reader = csv.DictReader(file_obj, delimiter=",")
        skipped_file_name = self.request.user.email
        file_name = re.search(r'\w+', skipped_file_name).group()
        response = {}

        error = False

        if not save_asset(csv_reader, file_name):

            path = request.build_absolute_uri(reverse('skipped'))

            response['fail'] = "Some assets were skipped." \
                               " Download the skipped assets file from"
            response['file'] = "{}".format(path)

            error = True

        response['success'] = "Asset import completed successfully "
        if error:
            response['success'] += "Assets that have not been imported" \
                "have been written to a file."
        return Response(data=response, status=200)


class SkippedAssets(APIView):
    def get(self, request):
        filename = os.path.join(settings.BASE_DIR,
                                "SkippedAssets/{}.csv".
                                format(re.search(r'\w+',
                                                 request.user.email).group()))

        # send file

        file = open(filename, 'rb')
        response = FileResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment;' \
            'filename="SkippedAssets.csv"'
        return response


class AndelaCentreViewset(ModelViewSet):
    serializer_class = AndelaCentreSerializer
    queryset = AndelaCentre.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)
