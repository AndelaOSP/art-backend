# Standard Library
import logging

# Third-Party Imports
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# App Imports
from api.authentication import FirebaseTokenAuthentication
from api.permissions import IsAdminReadOnly, IsSuperAdmin
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
    permission_classes = [IsAuthenticated, IsAdminReadOnly | IsSuperAdmin]
    authentication_classes = [FirebaseTokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated, IsAdminUser],
        serializer_class=OfficeBlockSerializer,
    )
    def office_blocks(self, request, pk=None):
        """This function adds a 'office_block` route to the andela-center
        route to show office blocks in a center.
         Args:
            request (obj): request object
            pk (str): id of a center
         Raises:
            PermissionDenied: If the user is not a super user
         Returns:
            dict: a list of block under a certain center
        """
        pk = self.kwargs.get("pk")
        if request.user.is_superuser or str(request.user.location.id) == pk:
            queryset = models.OfficeBlock.objects.filter(location_id=pk)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
        raise PermissionDenied(
            "Only a super Admin can view Office-blocks in other Centers"
        )


class OfficeBlockViewSet(ModelViewSet):
    serializer_class = OfficeBlockSerializer
    queryset = models.OfficeBlock.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ["get", "post"]

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
    http_method_names = ["get", "post"]

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
        if self.action == "retrieve":
            return DepartmentDetailSerializer
        return DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)
