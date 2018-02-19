from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    AssetCreateApiView, AssetGetUpdateDelete, CheckinCreateApiView,
    CheckoutCreateApiView
)

urlpatterns = {
    url(r'^art_api/assets/$', AssetCreateApiView.as_view(),
        name='create_assets'),
    url(r'^art_api/assets/(?P<pk>[0-9]+)/$', AssetGetUpdateDelete.as_view(),
        name='edit_assets'),
    url(r'^art_api/$', CheckinCreateApiView.as_view()),
    url(r'^art_api/assets/$', CheckoutCreateApiView.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
