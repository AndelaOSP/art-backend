# Third-Party Imports
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

# App Imports
from api.authentication import FirebaseTokenAuthentication
from api.serializers import HistorySerializer
from core import models


class HistoryViewSet(ModelViewSet):
    serializer_class = HistorySerializer
    queryset = models.History.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [FirebaseTokenAuthentication]
    http_method_names = ["get"]
