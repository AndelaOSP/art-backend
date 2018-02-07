from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AssetCreateApiView, AssetGetUpdateDelete, CheckinCreateApiView, CheckoutCreateApiView

urlpatterns = {
    url(r'^art_api/$', AssetCreateApiView.as_view()),
    url(r'^art_api/$', AssetGetUpdateDelete.as_view()),
    url(r'^art_api/$', CheckinCreateApiView.as_view()),
    url(r'^art_api/$', CheckoutCreateApiView.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
