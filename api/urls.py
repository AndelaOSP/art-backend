from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path

<<<<<<< HEAD
from .views import UserViewSet, ItemViewSet, SecurityUserEmailsViewSet
=======
from .views import UserViewSet, ItemViewSet, SecurityUserViewSet, \
    AssetLogViewSet
>>>>>>> fix(asset-log): refactor model naming

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')
<<<<<<< HEAD
router.register('security-user-emails',
                SecurityUserEmailsViewSet, 'security-user-emails')
=======
router.register('security_users', SecurityUserViewSet, 'security_users')
router.register('asset-log', AssetLogViewSet, 'asset-log')
>>>>>>> fix(asset-log): refactor model naming

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
]

urlpatterns += router.urls
