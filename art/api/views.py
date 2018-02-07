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
    """This creates, lists chekin entries"""
    serializer_class = CheckinLogsSerializer
    # To Add code with Josiah


"""checkout activity logic"""

class CheckoutCreateApiView(ListCreateAPIView):
    """This creates, lists chekin entries"""
    serializer_class = CheckoutLogsSerializer
    # To Add code with Josiah
