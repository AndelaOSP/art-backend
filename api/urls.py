from rest_framework.routers import SimpleRouter

from .views import UserViewSet, ItemViewSet, SecurityUserEmailsViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')
router.register('security_user_emails', SecurityUserEmailsViewSet, 'security_user_emails')
urlpatterns = router.urls
