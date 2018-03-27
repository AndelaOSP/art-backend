from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet, ItemViewSet, Login

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('items', ItemViewSet, 'items')
urlpatterns = [
    path('login/', Login.as_view())
]

urlpatterns += router.urls
