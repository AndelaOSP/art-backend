from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Asset, CheckinLogs, CheckoutLogs
from art.serializers import AssetSerializer, CheckinLogsSerializer, CheckoutLogsSerializer


class AssetCreateApiView(ListCreateAPIView):
    """Creates, lists item using user_id """
    serializer_class = AssetSerializer


class AssetGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    """ This gets, updates, deletes an asset using  the userid"""
    serializer_class = AssetSerializer


class CheckinCreateApiView(ListCreateAPIView):
    """This creates, lists chekin entries"""
    serializer_class = CheckinLogsSerializer


class CheckoutCreateApiView(ListCreateAPIView):
    """ This creates, lists chekout entries """
    serializer_class = CheckoutLogsSerializer

    def get_queryset(self):
        queryset = CheckoutLogs.objects.all()
        if(self.kwargs.get('pk')):
            queryset = queryset.filter(id=self.kwargs['pk'])
        return queryset

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
