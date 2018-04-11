from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from api.authentication import FirebaseTokenAuthentication
from .models import Item, SecurityUser
from .serializers import UserSerializer, \
    ItemSerializer, SecurityUserEmailsSerializer
from .permissions import IsApiUser

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get', 'post']


class ItemViewSet(ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (FirebaseTokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Item.objects.filter(assigned_to=user)

    def get_object(self):
        queryset = Item.objects.filter(assigned_to=self.request.user)
        obj = get_object_or_404(queryset, serial_number=self.kwargs['pk'])
        return obj


class SecurityUserEmailsViewSet(ModelViewSet):
    serializer_class = SecurityUserEmailsSerializer
    http_method_names = ['get']
    permission_classes = (IsApiUser, )

    def list(self, request, *args, **kwargs):

        list_of_emails = [security_user.email
                          for security_user in SecurityUser.objects.all()]

        return Response({'emails': list_of_emails}, status=status.HTTP_200_OK)
