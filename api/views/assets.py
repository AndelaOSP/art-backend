# Standard Library
import codecs
import csv
import logging
import os
import re
from itertools import chain

# Third-Party Imports
from django.conf import settings
from django.core.validators import ValidationError
from django.http import FileResponse
from django_filters import rest_framework as filters
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

# App Imports
from api.authentication import FirebaseTokenAuthentication
from api.filters import AssetFilter
from api.permissions import IsSecurityUser, IsLogUser
from api.serializers import (
    AllocationsSerializer,
    AssetAssigneeSerializer,
    AssetCategorySerializer,
    AssetConditionSerializer,
    AssetHealthSerializer,
    AssetIncidentReportSerializer,
    AssetLogSerializer,
    AssetMakeSerializer,
    AssetModelNumberSerializer,
    AssetSerializer,
    AssetSpecsSerializer,
    AssetStatusSerializer,
    AssetSubCategorySerializer,
    AssetTypeSerializer,
)
from core import models
from core.assets_saver_helper import save_asset
from core.management.commands.import_assets import SKIPPED_ROWS
from core.slack_bot import SlackIntegration

slack = SlackIntegration()
logger = logging.getLogger(__name__)


class ManageAssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    queryset = models.Asset.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssetFilter

    def get_object(self):
        queryset = models.Asset.objects.all()
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

    def perform_update(self, serializer):
        if serializer.validated_data.get('asset_location'):
            # check if it is a super user performing this
            if not self.request.user.is_superuser:
                raise PermissionDenied("Only a super user can update an asset location")
        serializer.save()

    def get_queryset(self):
        location = self.request.user.location
        if location:
            return self.queryset.filter(asset_location=location)
        return self.queryset.none()


class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        query_filter = {}
        if not hasattr(self.request.user, "securityuser"):
            asset_assignee = models.AssetAssignee.objects.filter(user=user).first()
            query_filter = {"assigned_to": asset_assignee}
        # filter through the query_parameters for serial_number and asset_code
        for field in self.request.query_params:
            if field == 'serial_number' or field == 'asset_code':
                query_filter[field] = self.request.query_params.get(field)
        queryset = models.Asset.objects.filter(**query_filter)
        return queryset

    def get_object(self):
        user = self.request.user
        asset_assignee = models.AssetAssignee.objects.filter(user=user).first()
        queryset = models.Asset.objects.filter(assigned_to=asset_assignee)
        obj = get_object_or_404(queryset, uuid=self.kwargs['pk'])
        return obj


class AssetAssigneeViewSet(ModelViewSet):
    serializer_class = AssetAssigneeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    queryset = models.AssetAssignee.objects.all()
    http_method_names = ['get']

    def get_queryset(self):
        user_location = self.request.user.location
        asset_assignees = []
        if user_location:
            for asset_assignee in self.queryset:
                if (
                    asset_assignee.user
                    and asset_assignee.user.location == user_location
                ):
                    asset_assignees.append(asset_assignee)
                if asset_assignee.department:
                    asset_assignees.append(asset_assignee)
                if (
                    asset_assignee.workspace
                    and asset_assignee.workspace.section.floor.block.location
                    == user_location
                ):
                    asset_assignees.append(asset_assignee)

            return asset_assignees
        return self.queryset.none()


class AssetLogViewSet(ModelViewSet):
    serializer_class = AssetLogSerializer
    queryset = models.AssetLog.objects.all()
    permission_classes = [IsLogUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user.securityuser)


class AssetStatusViewSet(ModelViewSet):
    serializer_class = AssetStatusSerializer
    queryset = models.AssetStatus.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()


class AllocationsViewSet(ModelViewSet):
    serializer_class = AllocationsSerializer
    queryset = models.AllocationHistory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()


class AssetCategoryViewSet(ModelViewSet):
    serializer_class = AssetCategorySerializer
    queryset = models.AssetCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ('category_name',)
    http_method_names = ['get', 'post']


class AssetSubCategoryViewSet(ModelViewSet):
    serializer_class = AssetSubCategorySerializer
    queryset = models.AssetSubCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ('sub_category_name',)
    http_method_names = ['get', 'post']


class AssetTypeViewSet(ModelViewSet):
    serializer_class = AssetTypeSerializer
    queryset = models.AssetType.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ('asset_type',)
    http_method_names = ['get', 'post']


class AssetModelNumberViewSet(ModelViewSet):
    serializer_class = AssetModelNumberSerializer
    queryset = models.AssetModelNumber.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    filter_backends = (OrderingFilter,)
    ordering = ('model_number',)
    http_method_names = ['get', 'post']


class AssetMakeViewSet(ModelViewSet):
    serializer_class = AssetMakeSerializer
    queryset = models.AssetMake.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    filter_backends = (OrderingFilter,)
    ordering = ('make_label',)
    http_method_names = ['get', 'post']


class AssetConditionViewSet(ModelViewSet):
    serializer_class = AssetConditionSerializer
    queryset = models.AssetCondition.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()


class AssetIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = models.AssetIncidentReport.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class AssetSlackIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = models.AssetIncidentReport.objects.all()
    http_method_names = ['post']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    def create(self, request, *args, **kwargs):
        if (self.request.data.get('command', None) is None) and (
            self.request.data.get('payload', None) is None
        ):
            try:
                response = super().create(request, *args, **kwargs)
            except ValidationError as err:
                raise serializers.ValidationError(err.error_dict)
            return response
        else:
            bot = slack.send_incidence_report(
                self.request.data, models.Asset, models.AssetIncidentReport, models.User
            )
            if bot:
                return Response(status=status.HTTP_200_OK)


class AssetHealthCountViewSet(ModelViewSet):
    serializer_class = AssetHealthSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']
    queryset = models.Asset.objects.all()
    data = None

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset_location=user_location)
        return self.queryset.none()

    def _get_assets_status_condition(self, asset_models):
        asset_name, model_numbers = asset_models.popitem()

        def generate_asset_condition(model_number):
            statuses = {'Allocated': 0, 'Available': 0, 'Damaged': 0, 'Lost': 0}

            def increment_asset_status(asset, model_number=model_number):
                if (
                    asset['asset_type'] == asset_name
                    and asset['model_number'] == model_number
                ):
                    nonlocal statuses
                    statuses[asset['count_by_status']] += 1
                return statuses

            list(map(increment_asset_status, self.data))
            return {
                'asset_type': asset_name,
                'model_number': model_number,
                'count_by_status': statuses,
            }

        return list(map(generate_asset_condition, model_numbers))

    def _get_asset_list(self, asset):
        asset_with_status = list(map(self._get_assets_status_condition, asset))
        return list(chain.from_iterable(asset_with_status))

    def _get_asset_type(self, asset):
        return asset['asset_type']

    def _get_model_numbers(self, asset_type):
        asset_model_numbers = map(
            lambda asset: asset['model_number'],
            filter(lambda asset: asset['asset_type'] == asset_type, self.data),
        )
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
        return Response(
            exception=True,
            status=403,
            data={'detail': ['You do not have authorization']},
        )


class AssetSpecsViewSet(ModelViewSet):
    serializer_class = AssetSpecsSerializer
    queryset = models.AssetSpecs.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post', 'put']


class AssetsImportViewSet(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file_obj = request.data.get('file')
        if not file_obj:
            # file_obj is none so return error
            return Response(
                {"error": "Csv file to import from not provided"}, status=400
            )

        file_obj = codecs.iterdecode(file_obj, 'utf-8')
        csv_reader = csv.DictReader(file_obj, delimiter=",")
        skipped_file_name = self.request.user.email
        file_name = re.search(r'\w+', skipped_file_name).group()
        response = {}

        error = False

        if not save_asset(csv_reader, file_name):
            path = request.build_absolute_uri(reverse('skipped'))

            response[
                'fail'
            ] = "Some assets were skipped. Download the skipped assets file from"
            response['file'] = "{}".format(path)

            error = True

        response['success'] = "Asset import completed successfully "
        if error:
            response[
                'success'
            ] += "Assets that have not been imported have been written to a file."
        del SKIPPED_ROWS[:]
        return Response(data=response, status=200)


class SkippedAssets(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        filename = os.path.join(
            settings.BASE_DIR,
            "SkippedAssets/{}.csv".format(
                re.search(r'\w+', request.user.email).group()
            ),
        )

        # send file

        file = open(filename, 'rb')
        response = FileResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="SkippedAssets.csv"'

        return response


class SampleImportFile(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        filename = os.path.join(settings.BASE_DIR, "Samples/sample_import.csv")

        # send file

        file = open(filename, 'rb')
        response = FileResponse(file, content_type='text/csv')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="sample_import_file.csv"'

        return response
