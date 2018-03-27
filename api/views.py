from django.conf import settings
from django.contrib.auth import get_user_model
from oauth2client import client, crypt
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
    def verify_google_token(id_token):
        is_token_valid = True
        try:
            id_info = client.verify_id_token(id_token, settings.CLIENT_ID)

            if id_info['iss'] not in \
                    ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
            if not id_info['email']:
                return Response({
                    'message': "Allow user email info",
                }, status=HTTP_400_BAD_REQUEST)

        except crypt.AppIdentityError:
            is_token_valid = False
            id_info = {
                'Response': "Invalid token",
            }
        return is_token_valid, id_info

    def post(self, request):

        id_token = request.data.get('id_token') or ''
        is_token_valid, google_response = self.verify_google_token(id_token)
        if is_token_valid:

            try:
                email = google_response.get('email')
                if not google_response.get('hd') == 'andela.com':
                    return Response({
                        'message': "Must login with andelan email",
                    }, status=HTTP_400_BAD_REQUEST)
                user = User.objects.get(email=email)
                token = Token.objects.get(user=user)
                status_code = HTTP_202_ACCEPTED
            except User.DoesNotExist:
                picture = google_response.get('picture')
                email = google_response.get('email')
                f_name = google_response.get('given_name')
                l_name = google_response.get('family_name')

                user = User.objects.create(
                    email=email, first_name=f_name,
                    last_name=l_name, picture=picture
                )
                token = Token.objects.create(user=user)
                status_code = HTTP_201_CREATED

            additional_content = {
                'token': token.key,
            }
            return Response(additional_content, status_code)
        else:
            return Response(google_response, status=HTTP_400_BAD_REQUEST)
