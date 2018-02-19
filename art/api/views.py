from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Asset, CheckinLogs, CheckoutLogs
from art.serializers import AssetSerializer, CheckinLogsSerializer, CheckoutLogsSerializer

class AssetCreateApiView(ListCreateAPIView):
    """Creates, lists item using user_id """
    
    serializer_class = AssetSerializer
    # To Add code with Josiah

class AssetGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    """ This gets, updates, deletes an asset using  the userid"""
    serializer_class = AssetSerializer
    # To Add code with Josiah

"""Checkin activity logic"""

class CheckinCreateApiView(ListCreateAPIView):
    """
    perform_create
    saves a checkin log for a user

    get_queryset:
    list a checkin log for a user
    """

    serializer_class = CheckinLogsSerializer

    def perform_create(self, serializer):

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = CheckinLogs.objects.all()
        if 'pk' in self.kwargs:
            queryset = queryset.filter(id=self.kwargs['pk'])
        return queryset

"""checkout activity logic"""

class CheckoutCreateApiView(ListCreateAPIView):
    """This creates, lists chekin entries"""
    serializer_class = CheckoutLogsSerializer
    # To Add code with Josiah
