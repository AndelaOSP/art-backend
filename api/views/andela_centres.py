# Standard Library
import logging

# Third-Party Imports
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# App Imports
from api.authentication import FirebaseTokenAuthentication
from api.serializers import (
    AndelaCentreSerializer,
    CountrySerializer,
    DepartmentDetailSerializer,
    DepartmentSerializer,
    OfficeBlockSerializer,
    OfficeFloorSectionSerializer,
    OfficeFloorSerializer,
    OfficeWorkspaceSerializer,
)
from core import models

logger = logging.getLogger(__name__)


class CountryViewset(ModelViewSet):
    serializer_class = CountrySerializer
    queryset = models.Country.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]


class AndelaCentreViewset(ModelViewSet):
    serializer_class = AndelaCentreSerializer
    queryset = models.AndelaCentre.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class OfficeBlockViewSet(ModelViewSet):
    serializer_class = OfficeBlockSerializer
    queryset = models.OfficeBlock.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(location=user_location)
        return self.queryset.none()


class OfficeFloorViewSet(ModelViewSet):
    serializer_class = OfficeFloorSerializer
    queryset = models.OfficeFloor.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(block__location=user_location)
        return self.queryset.none()


class OfficeFloorSectionViewSet(ModelViewSet):
    serializer_class = OfficeFloorSectionSerializer
    queryset = models.OfficeFloorSection.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(floor__block__location=user_location)
        return self.queryset.none()


class OfficeWorkspaceViewSet(ModelViewSet):
    serializer_class = OfficeWorkspaceSerializer
    queryset = models.OfficeWorkspace.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = models.Department.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)
