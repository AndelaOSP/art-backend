from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AssetCreateApiView, AssetGetUpdateDelete, CheckinCreateApiView, CheckoutCreateApiView

urlpatterns = {
    url(r'^art_api/$', AssetCreateApiView.as_view()),
    url(r'^art_api/$', AssetGetUpdateDelete.as_view()),
    url(r'^art_api/checkin', CheckinCreateApiView.as_view(), name="create-checkin"),
    url(r'^art_api/checkin/(?P<pk>[0-9]+)$', CheckinCreateApiView.as_view(), name="get-checkin"),
    url(r'^art_api/$', CheckoutCreateApiView.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
