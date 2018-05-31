from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


from .views import UserViewSet, AssetViewSet, SecurityUserEmailsViewSet, \
    AssetLogViewSet, UserFeedbackViewSet, AssetStatusViewSet,\
    AllocationsViewSet, AssetCategoryViewSet, AssetSubCategoryViewSet, \
    AssetTypeViewSet, AssetModelNumberViewSet, AssetConditionViewSet, \
    AssetMakeViewSet, AssetIncidentReportViewSet, AssetHealthCountViewSet


schema_view = get_schema_view(
    openapi.Info(
        title='ART API',
        default_version='v1',
        description='Assset tracking',
        license=openapi.License(name='BSD License'),
    ),
    public=True,
)

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
router.register('asset-condition', AssetConditionViewSet,
                'asset-condition')
router.register('asset-makes', AssetMakeViewSet, 'asset-makes')
router.register('incidence-reports', AssetIncidentReportViewSet,
                'incidence-reports')
router.register('asset-health', AssetHealthCountViewSet, 'asset-health')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('docs/', schema_view.with_ui(
        'redoc', cache_timeout=None), name='schema-redoc'),
    path('docs/live/', schema_view.with_ui(
        'swagger', cache_timeout=None), name='schema-swagger')
]

urlpatterns += router.urls
