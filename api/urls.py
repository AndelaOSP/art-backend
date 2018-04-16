from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path


from .views import UserViewSet, ItemViewSet, SecurityUserEmailsViewSet, \
    AssetLogViewSet, UserFeedbackViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')
router.register('security-user-emails',
                SecurityUserEmailsViewSet, 'security-user-emails')
router.register('asset-logs', AssetLogViewSet, 'asset-logs')
router.register('user-feedback', UserFeedbackViewSet, 'user-feedback')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
]

urlpatterns += router.urls
