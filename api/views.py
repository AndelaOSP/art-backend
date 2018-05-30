from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
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
    AssetMakeSerializer, AssetIncidentReportSerializer
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
        if not is_admin:
            return Asset.objects.filter(assigned_to=user)
        return Asset.objects.all()

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
    authentication_classes = (FirebaseTokenAuthentication, )
    http_method_names = ['get', 'post']


class AssetIncidentReportViewSet(ModelViewSet):
    serializer_class = AssetIncidentReportSerializer
    queryset = AssetIncidentReport.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post']
