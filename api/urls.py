from rest_framework.routers import SimpleRouter

from .views import UserViewSet

router = SimpleRouter()
router.register('api/v1/user', UserViewSet)
urlpatterns = router.urls
