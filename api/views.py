from django.contrib.auth import get_user_model
from firebase_admin import auth
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_202_ACCEPTED
)
from .models import Item
from .serializers import UserSerializer, ItemSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (TokenAuthentication,)
    http_method_names = ['get', 'post']


class ItemViewSet(ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, ]
    authentication_classes = (TokenAuthentication,)
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Item.objects.filter(assigned_to=user)


class Login(APIView):
    @staticmethod
    def verify_token(id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            is_token_valid = True
        except ValueError:
            is_token_valid = False
            is_token_valid = False
            decoded_token = {
                'Response': "Invalid token",
            }
        return is_token_valid, decoded_token

    def post(self, request):
        id_token = request.data.get('id_token') or ''
        is_token_valid, decoded_token = self.verify_token(id_token)
        if is_token_valid:
            try:

                email = decoded_token['email']
                user = User.objects.get(email=email)
                token = Token.objects.get(user=user)
                status_code = HTTP_202_ACCEPTED
            except User.DoesNotExist:
                picture = decoded_token.get('picture')
                email = decoded_token.get('email')

                user = User.objects.create(
                    email=email, picture=picture
                )
                token = Token.objects.create(user=user)
                status_code = HTTP_201_CREATED
            additional_content = {
                'token': token.key,
            }
            return Response(additional_content, status_code)
        else:
            return Response(decoded_token, status=HTTP_400_BAD_REQUEST)
