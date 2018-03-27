from rest_framework.routers import SimpleRouter

from .views import UserViewSet, ItemViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')

urlpatterns = router.urls
