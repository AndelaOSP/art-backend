from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Asset, CheckinLogs, CheckoutLogs
from art.serializers import (
    AssetSerializer, CheckinLogsSerializer, CheckoutLogsSerializer
)


class AssetCreateApiView(ListCreateAPIView):
    """This class creates new assets and lists all assets """

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def post(self, request):
        if Asset.objects.filter(full_name=self.request.data.get(
                'full_name')).first():
            response = Response({
                "Failed": "This person already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(mac_book_sn=self.request.data.get(
                'mac_book_sn')).first():
            response = Response({
                "Failed": "Macbook Serial Number already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(mac_book_tag=self.request.data.get(
                'mac_book_tag')).first():
            response = Response({
                "Failed": "Macbook tag already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(charger_tag=self.request.data.get(
                'charger_tag')).first():
            response = Response({
                "Failed": "Charger tag already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(tb_dongle_tag=self.request.data.get(
                'tb_dongle_tag')).first():
            response = Response({
                "Failed": "Dongle tag already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(headsets_sn=self.request.data.get(
                'headsets_sn')).first():
            response = Response({
                "Failed": "Headsets serial number already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        elif Asset.objects.filter(headsets_tag=self.request.data.get(
                'headsets_tag')).first():
            response = Response({
                "Failed": "Headsets tag already exists"
            },
                status=status.HTTP_409_CONFLICT
            )
        else:
            response = self.create(request)

        return response

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AssetGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    """ This class gets, updates, deletes an asset using  the userid"""
    serializer_class = AssetSerializer
    queryset = Asset.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CheckinCreateApiView(ListCreateAPIView):
    """This creates, lists chekin entries"""
    serializer_class = CheckinLogsSerializer
    # To Add code with Josiah


"""checkout activity logic"""


class CheckoutCreateApiView(ListCreateAPIView):
    """This creates, lists chekin entries"""
    serializer_class = CheckoutLogsSerializer
    # To Add code with Josiah
