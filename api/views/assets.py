# Standard Library
import codecs
import functools
import logging
import operator
import os
from itertools import chain

# Third-Party Imports
import xlsxwriter
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import ValidationError
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import FileResponse
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
from api.filters import AllocationsHistoryFilter, AssetFilter, AssetLogFilter
from api.permissions import IsSecurityUser
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
    StateTransitionSerializer,
)
from core import models
from core.assets_import_helper import DictReaderStrip, process_file, SKIPPED_ROWS
from core.constants import (
    ASSET_CODE,
    ASSIGNED_TO,
    CSV_HEADERS,
    CSV_REQUIRED_HEADING_ASSET_CODE,
    CSV_REQUIRED_HEADING_SERIAL_NO,
    MAKE,
    MODEL_NUMBER,
    NOTES,
    SERIAL_NUMBER,
    STATUS,
    VERIFIED,
)
from core.models.asset import user_abstract
from core.slack_bot import SlackIntegration

slack = SlackIntegration()
logger = logging.getLogger(__name__)


class ManageAssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    queryset = models.Asset.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    filterset_class = AssetFilter

    def get_object(self):
        queryset = models.Asset.objects.all()
        obj = get_object_or_404(queryset, uuid=self.kwargs["pk"])
        return obj

    def _restrict_to_only_super_users(self, invoice_receipt, user):
        if invoice_receipt and not user.is_superuser:
            raise PermissionDenied("Only a super admin can add an invoice_receipt")

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
        except ValidationError as err:
            raise serializers.ValidationError(err.error_dict)
        return response

    def perform_create(self, serializer):

        self._restrict_to_only_super_users(
            serializer.validated_data.get("invoice_receipt"), self.request.user
        )

        serializer.save(asset_location=self.request.user.location)

    def perform_update(self, serializer):

        self._restrict_to_only_super_users(
            serializer.validated_data.get("invoice_receipt"), self.request.user
        )
        serializer.instance.invoice_receipt.delete(save=False)

        if serializer.validated_data.get("asset_location"):
            # check if it is a super user performing this
            if not self.request.user.is_superuser:
                raise PermissionDenied("Only a super user can update an asset location")
        serializer.save()

    def get_queryset(self):
        location = self.request.user.location
        department = self.request.user.department
        if location and department:
            return self.queryset.filter(asset_location=location, department=department)
        return self.queryset.none()


class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ["get"]

    def get_queryset(self):
        user = self.request.user
        query_filter = {}

        if not self.request.user.is_securityuser:
            asset_assignee = models.AssetAssignee.objects.filter(user=user).first()
            query_filter = {"assigned_to": asset_assignee}
        # filter through the query_parameters for serial_number and asset_code
        for field in self.request.query_params:
            if field == "serial_number" or field == "asset_code":
                query_filter[field] = self.request.query_params.get(field)
        queryset = models.Asset.objects.filter(**query_filter)
        return queryset

    def get_object(self):
        user = self.request.user
        asset_assignee = models.AssetAssignee.objects.filter(user=user).first()
        queryset = models.Asset.objects.filter(assigned_to=asset_assignee)
        obj = get_object_or_404(queryset, uuid=self.kwargs["pk"])
        return obj


class AssetAssigneeViewSet(ModelViewSet):
    serializer_class = AssetAssigneeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    queryset = models.AssetAssignee.objects.all()
    http_method_names = ["get"]

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
    permission_classes = [IsAdminUser | IsSecurityUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    filterset_class = AssetLogFilter
    http_method_names = ["get", "post"]

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user)


class AssetStatusViewSet(ModelViewSet):
    serializer_class = AssetStatusSerializer
    queryset = models.AssetStatus.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ["get", "post"]

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
    filterset_class = AllocationsHistoryFilter
    http_method_names = ["get", "post"]

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(assigner=self.request.user)


class AssetCategoryViewSet(ModelViewSet):
    serializer_class = AssetCategorySerializer
    queryset = models.AssetCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ("name",)


class AssetSubCategoryViewSet(ModelViewSet):
    serializer_class = AssetSubCategorySerializer
    queryset = models.AssetSubCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ("name",)


class AssetTypeViewSet(ModelViewSet):
    serializer_class = AssetTypeSerializer
    queryset = models.AssetType.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    filter_backends = (OrderingFilter,)
    ordering = ("name",)


class AssetModelNumberViewSet(ModelViewSet):
    serializer_class = AssetModelNumberSerializer
    queryset = models.AssetModelNumber.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    filter_backends = (OrderingFilter,)
    ordering = ("name",)


class AssetMakeViewSet(ModelViewSet):
    serializer_class = AssetMakeSerializer
    queryset = models.AssetMake.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseTokenAuthentication]
    filter_backends = (OrderingFilter,)
    ordering = ("name",)


class AssetConditionViewSet(ModelViewSet):
    serializer_class = AssetConditionSerializer
    queryset = models.AssetCondition.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location)
        return self.queryset.none()


class AssetIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = models.AssetIncidentReport.objects.all()
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(asset__asset_location=user_location).order_by(
                "created_at"
            )
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class AssetSlackIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = models.AssetIncidentReport.objects.all()
    http_method_names = ["post"]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    def create(self, request, *args, **kwargs):
        if (self.request.data.get("command", None) is None) and (
            self.request.data.get("payload", None) is None
        ):
            try:
                response = super().create(request, *args, **kwargs)
            except ValidationError as err:
                raise serializers.ValidationError(err.error_dict)
            return response
        else:
            bot = slack.send_incidence_report(self.request.data)
            if bot:
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AssetHealthCountViewSet(ModelViewSet):
    serializer_class = AssetHealthSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ["get"]
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
            statuses = {"Allocated": 0, "Available": 0, "Damaged": 0, "Lost": 0}

            def increment_asset_status(asset, model_number=model_number):
                if (
                    asset.get("asset_type") == asset_name
                    and asset.get("model_number") == model_number
                ):
                    nonlocal statuses
                    statuses[asset["count_by_status"]] += 1
                return statuses

            list(map(increment_asset_status, self.data))
            return {
                "asset_type": asset_name,
                "model_number": model_number,
                "count_by_status": statuses,
            }

        return list(map(generate_asset_condition, model_numbers))

    def _get_asset_list(self, asset):
        asset_with_status = list(map(self._get_assets_status_condition, asset))
        return list(chain.from_iterable(asset_with_status))

    def _get_asset_type(self, asset):
        return asset["asset_type"]

    def _get_model_numbers(self, asset_type):
        asset_model_numbers = map(
            lambda asset: asset.get("model_number"),
            filter(lambda asset: asset.get("asset_type") == asset_type, self.data),
        )
        return {asset_type: set(list(asset_model_numbers))}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        self.data = serializer.data
        asset_types = set(map(self._get_asset_type, self.data))
        asset = map(self._get_model_numbers, asset_types)
        asset_list = self._get_asset_list(asset)
        return Response(asset_list)


class AssetSpecsViewSet(ModelViewSet):
    serializer_class = AssetSpecsSerializer
    queryset = models.AssetSpecs.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]


class AssetsImportViewSet(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file_object = request.data.get("file")
        if not file_object:
            # file_obj is none so return error
            return Response(
                {"error": "Csv file to import from not provided"}, status=400
            )
        if not file_object.name.endswith(".csv"):
            return Response(
                {"error": "File type not surported, import a CSV file"}, status=400
            )
        file_obj = codecs.iterdecode(file_object, "utf-8")
        csv_reader = DictReaderStrip(file_obj, delimiter=",")
        if not (csv_reader.fieldnames and " ".join(csv_reader.fieldnames).strip()):
            return Response({"error": "CSV file is empty"}, status=400)
        field_names_set = set(csv_reader.fieldnames)
        if not field_names_set.issubset(CSV_HEADERS):
            return Response({"error": "CSV file contains invalid headings"}, status=400)
        if not (
            field_names_set >= CSV_REQUIRED_HEADING_ASSET_CODE
            or field_names_set >= CSV_REQUIRED_HEADING_SERIAL_NO
        ):
            return Response({"error": "File contains missing headings"}, status=400)
        csv_values = []
        for line in csv_reader.reader:
            line = [val for val in line if val and val.strip()]
            csv_values = csv_values + line
        csv_values = list(set(csv_values))
        if not csv_values:
            return Response({"error": "CSV file only contains headings"}, status=400)
        user = self.request.user
        response = {}
        error = False
        file_obj = codecs.iterdecode(file_object, "utf-8")
        csv_reader = DictReaderStrip(file_obj, delimiter=",")
        print("Processing uploaded file:")
        if not process_file(csv_reader, user=user):
            filename = user.email.split("@")[0]
            path = request.build_absolute_uri(reverse("download-files"))
            print("path in main end point", path)

            response[
                "fail"
            ] = "Some assets were skipped. Download the skipped assets file from"
            response["file"] = "{}".format(path)
            response["filename"] = f"{filename}"

            error = True

        response["success"] = "Asset import completed successfully "
        if error:
            response[
                "success"
            ] += "Assets that have not been imported have been written to a file."
        del SKIPPED_ROWS[:]
        return Response(data=response, status=200)


class FileDownloads(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        query_dict = request.query_params.dict()
        filename = ""

        try:
            filename = query_dict.get("filename")
            if filename:
                file_path = os.path.join(settings.BASE_DIR, f"files/{filename}")
                file = open(file_path, "rb")

        except FileNotFoundError:
            return Response({"response": f"No such file or directory as {filename}"})

        else:
            response = FileResponse(file, content_type="text/csv", filename=filename)
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response


class ExportAssetsDetails(APIView):
    serializer_class = AssetSerializer
    queryset = models.Asset.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (FirebaseTokenAuthentication,)

    def get(self, request):
        filters = Q(**{})
        for key, val in dict(request.query_params).items():
            lookup = functools.reduce(
                operator.or_,
                {Q(**{"__".join([key, "icontains"]): item}) for item in val},
            )
            filters |= lookup
        try:
            assets = self.queryset.filter(
                filters, asset_location__name=request.user.location.name
            )
        except Exception as e:
            logger.warning(str(e))
            return Response({"error": "Unsupported filters included."}, status=400)
        serializer = self.serializer_class(assets, many=True)
        asset_count = len(serializer.data)
        if asset_count == 0:
            return Response({"error": "You have no assets"}, status=400)

        email = request.user.email
        filename = "files/{}_exported_assets.xlsx".format(email.split("@")[0])
        self.create_sheet(serializer.data, filename=filename)
        path = request.build_absolute_uri(reverse("download-files"))
        return Response(
            {
                "success": f"{asset_count} assets exported to {path} successfully",
                "file": path,
            },
            status=200,
        )

    def create_sheet(self, assets_list, filename=None):
        asset_types = []
        filename = filename or "exported_assets.xlsx"
        for asset in assets_list:
            if asset.get("asset_type") not in asset_types:
                asset_types.append(asset.get("asset_type"))

        workbook = xlsxwriter.Workbook(filename)
        bold = workbook.add_format({"bold": True, "bg_color": "silver"})
        for asset_type in asset_types:
            worksheet = workbook.add_worksheet(asset_type)
            worksheet.write("A1", MAKE, bold)
            worksheet.write("B1", "Location", bold)
            worksheet.write("C1", ASSET_CODE, bold)
            worksheet.write("D1", SERIAL_NUMBER, bold)
            worksheet.write("E1", MODEL_NUMBER, bold)
            worksheet.write("F1", ASSIGNED_TO, bold)
            worksheet.write("G1", STATUS, bold)
            worksheet.write("H1", VERIFIED, bold)
            worksheet.write("I1", NOTES, bold)
            grouped_assets = []
            for asset in assets_list:
                if asset.get("asset_type") == asset_type:
                    grouped_assets.append(asset)
            row = 1
            column = 0
            for asset in grouped_assets:
                worksheet.write(row, column, asset.get("asset_make", ""))
                worksheet.write(row, column + 1, asset.get("asset_location", ""))
                worksheet.write(row, column + 2, asset.get("asset_code"))
                worksheet.write(row, column + 3, asset.get("serial_number", ""))
                worksheet.write(row, column + 4, asset.get("model_number", ""))
                assigned = asset.get("assigned_to") or {}
                assignee = assigned.get("email", "")
                worksheet.write(row, column + 5, assignee)
                worksheet.write(row, column + 6, asset.get("current_status", ""))
                worksheet.write_boolean(row, column + 7, asset.get("verified", ""))
                worksheet.write(row, column + 8, asset.get("notes", ""))
                row += 1
        workbook.close()


class StateTransitionViewset(ModelViewSet):
    serializer_class = StateTransitionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    queryset = models.StateTransition.objects.all()

    def perform_update(self, serializer):

        report_state = self.request.data.get("incident_report_state", None)
        asset_state = self.request.data.get("asset_state_from_report", None)
        if (
            report_state == "external assessment"
            and asset_state == "requires external assessment"
        ):
            raise serializers.ValidationError(
                {"Error": "Asset state option is not valid for given report state"}
            )

        try:
            serializer.save(
                incident_report_state=report_state,
                asset_state_from_report=asset_state,
                partial=True,
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    "Error": "Ensure that incident_report_state\
                    and asset_state_from_report fields are filled".replace(
                        " " * 20, " "
                    )
                }
            )

class PoliceAbstract(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        abstract = request.FILES.get('police_abstract', None)
        if abstract:
            user = request.user
            abstract_name = user_abstract(user, abstract.name)
            user.police_abstract = abstract_name
            user.save()
            fs = FileSystemStorage()
            filename = fs.save(abstract_name, abstract)
            uploaded_file_url = fs.url(filename)

            return Response(
                data={"success": {"uploaded_file_url": uploaded_file_url}}
            )
        else:
            return ValidationError("Abstract not provided")
