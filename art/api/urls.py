from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AssetCreateApiView, AssetGetUpdateDelete, CheckinCreateApiView, CheckoutCreateApiView

urlpatterns = {
    url(r'^art_api/$', AssetCreateApiView.as_view()),
    url(r'^art_api/$', AssetGetUpdateDelete.as_view()),
    url(r'^art_api/$', CheckinCreateApiView.as_view()),
    url(r'^art_api/checkout$', CheckoutCreateApiView.as_view()),
    url(r'^art_api/checkout/(?P<pk>[0-9]+)$',
        CheckoutCreateApiView.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
