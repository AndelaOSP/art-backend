from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import Item
from .serializers import UserSerializer, ItemSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    http_method_names = ['get', 'post']


class ItemViewSet(ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Item.objects.filter(assigned_to=user)

    def get_object(self):
        queryset = Item.objects.filter(assigned_to=self.request.user)
        obj = get_object_or_404(queryset, serial_number=self.kwargs['pk'])
        return obj
