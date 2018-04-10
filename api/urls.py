from rest_framework.routers import SimpleRouter

from .views import UserViewSet, ItemViewSet, SecurityUserViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')
router.register('security_users', SecurityUserViewSet, 'security_users')
urlpatterns = router.urls
