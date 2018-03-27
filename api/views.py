from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from api.authentication import FirebaseTokenAuthentication
from .models import Item
from .serializers import UserSerializer, ItemSerializer

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
