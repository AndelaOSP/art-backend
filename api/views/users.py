# Standard Library
import logging

# Third-Party Imports
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django_filters import rest_framework as filters
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

# App Imports
from api.authentication import FirebaseTokenAuthentication
from api.filters import UserFilter
from api.permissions import IsApiUser
from api.serializers import (SecurityUserEmailsSerializer, SecurityUserSerializer, UserFeedbackSerializer,
                             UserGroupSerializer, UserSerializerWithAssets)
from core import models

logger = logging.getLogger(__name__)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializerWithAssets
    queryset = models.User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        location = self.request.user.location
        if location:
            return self.queryset.filter(location=location)
        return self.queryset.none()


class SecurityUserEmailsViewSet(ModelViewSet):
    serializer_class = SecurityUserEmailsSerializer
    http_method_names = ['get']
    permission_classes = (IsApiUser,)

    def list(self, request, *args, **kwargs):
        list_of_emails = [security_user.email
                          for security_user in models.SecurityUser.objects.all()]

        return Response({'emails': list_of_emails}, status=status.HTTP_200_OK)


class UserFeedbackViewSet(ModelViewSet):
    serializer_class = UserFeedbackSerializer
    queryset = models.UserFeedback.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class SecurityUserViewSet(ModelViewSet):
    serializer_class = SecurityUserSerializer
    queryset = models.SecurityUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication, ]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        user_location = self.request.user.location
        if user_location:
            return self.queryset.filter(location=user_location)
        return self.queryset.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"detail": "Deleted Successfully"}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(SecurityUserViewSet, self).update(request, *args, **kwargs)


class UserGroupViewSet(ModelViewSet):
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


class AvailableFilterValues(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]

    def get(self, request):
        cohorts = set()
        asset_count = set()
        for user in models.User.objects.all():
            cohorts.add(user.cohort)
            try:
                assignee_asset_count = user.assetassignee.asset_set.count()
            except Exception as e:
                logger.warning('Error: {}. User: {}'.format(str(e), user.id))
            else:
                asset_count.add(assignee_asset_count)
        cohort_res = [{"id": cohort, "option": cohort}
                      for cohort in cohorts if cohort is not None]
        asset_num = [{"id": count, "option": count}
                     for count in asset_count if count is not None]
        return Response(data={"cohorts": cohort_res, "asset_count": asset_num}, status=200)
