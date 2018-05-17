from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path


from .views import UserViewSet, AssetViewSet, SecurityUserEmailsViewSet, \
    AssetLogViewSet, UserFeedbackViewSet, AssetStatusViewSet,\
    AllocationsViewSet, AssetCategoryViewSet, AssetSubCategoryViewSet, \
    AssetTypeViewSet, AssetModelNumberViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('assets', AssetViewSet, 'assets')
router.register('allocations', AllocationsViewSet, 'allocations')
router.register('security-user-emails',
                SecurityUserEmailsViewSet, 'security-user-emails')
router.register('asset-logs', AssetLogViewSet, 'asset-logs')
router.register('user-feedback', UserFeedbackViewSet, 'user-feedback')
router.register('asset-status', AssetStatusViewSet, 'asset-status')
router.register('asset-categories', AssetCategoryViewSet, 'asset-categories')
router.register('asset-sub-categories', AssetSubCategoryViewSet,
                'asset-sub-categories')
router.register('asset-types', AssetTypeViewSet,
                'asset-types')
router.register('asset-models', AssetModelNumberViewSet,
                'asset-models')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
]

urlpatterns += router.urls
