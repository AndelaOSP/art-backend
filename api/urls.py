# Third-Party Imports
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import SimpleRouter

# App Imports
from api.views import (
    AllocationsViewSet,
    AndelaCentreViewset,
    AssetAssigneeViewSet,
    AssetCategoryViewSet,
    AssetConditionViewSet,
    AssetHealthCountViewSet,
    AssetIncidentReportViewSet,
    AssetLogViewSet,
    AssetMakeViewSet,
    AssetModelNumberViewSet,
    AssetsImportViewSet,
    AssetSlackIncidentReportViewSet,
    AssetSpecsViewSet,
    AssetStatusViewSet,
    AssetSubCategoryViewSet,
    AssetTypeViewSet,
    AssetViewSet,
    AvailableFilterValues,
    CountryViewset,
    DepartmentViewSet,
    ExportAssetsDetails,
    GetPrintAssetsFile,
    ManageAssetViewSet,
    OfficeBlockViewSet,
    OfficeFloorSectionViewSet,
    OfficeFloorViewSet,
    OfficeWorkspaceViewSet,
    SampleImportFile,
    SecurityUserEmailsViewSet,
    SecurityUserViewSet,
    SkippedAssets,
    StateTransitionViewset,
    UserFeedbackViewSet,
    UserGroupViewSet,
    UserViewSet,
)

schema_view = get_schema_view(
    openapi.Info(
        title="ART API",
        default_version="v1",
        description="Assset tracking",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


class OptionalSlashRouter(SimpleRouter):
    def __init__(self, trailing_slash="/?"):
        self.trailing_slash = trailing_slash
        super(SimpleRouter, self).__init__()


router = OptionalSlashRouter()

# users
router.register(
    "security-user-emails", SecurityUserEmailsViewSet, "security-user-emails"
)
router.register("security-users", SecurityUserViewSet, "security-users")
router.register("user-feedback", UserFeedbackViewSet, "user-feedback")
router.register("user-groups", UserGroupViewSet, "user-groups")
router.register("users", UserViewSet, "users")

# assets
router.register("allocations", AllocationsViewSet, "allocations")
router.register("assets", AssetViewSet, "assets")
router.register("asset-assignee", AssetAssigneeViewSet, "asset-assignee")
router.register("asset-logs", AssetLogViewSet, "asset-logs")
router.register("asset-categories", AssetCategoryViewSet, "asset-categories")
router.register("asset-condition", AssetConditionViewSet, "asset-condition")
router.register("asset-health", AssetHealthCountViewSet, "asset-health")
router.register("asset-makes", AssetMakeViewSet, "asset-makes")
router.register("asset-models", AssetModelNumberViewSet, "asset-models")
router.register("asset-specs", AssetSpecsViewSet, "asset-specs")
router.register("asset-status", AssetStatusViewSet, "asset-status")
router.register("asset-sub-categories", AssetSubCategoryViewSet, "asset-sub-categories")
router.register("asset-types", AssetTypeViewSet, "asset-types")
router.register("incidence-reports", AssetIncidentReportViewSet, "incidence-reports")
router.register("manage-assets", ManageAssetViewSet, "manage-assets")
router.register(
    "slack-incidence-reports",
    AssetSlackIncidentReportViewSet,
    "slack-incidence-reports",
)
router.register("state-transitions", StateTransitionViewset, "state-transitions")

# centres
router.register("andela-centres", AndelaCentreViewset, "andela-centres")
router.register("countries", CountryViewset, "countries")
router.register("departments", DepartmentViewSet, "departments")
router.register("office-blocks", OfficeBlockViewSet, "office-blocks")
router.register("office-floors", OfficeFloorViewSet, "office-floors")
router.register("office-sections", OfficeFloorSectionViewSet, "floor-sections")
router.register("office-workspaces", OfficeWorkspaceViewSet, "office-workspaces")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path(
        "",
        TemplateView.as_view(
            template_name="api/api-index.html", extra_context={"api_version": "V1"}
        ),
        name="api-version-index",
    ),
    path("export-assets/", ExportAssetsDetails.as_view(), name="export-assets"),
    path("asset-details/", GetPrintAssetsFile.as_view(), name="asset-details"),
    path("upload/", AssetsImportViewSet.as_view(), name="import-assets"),
    path("skipped/", SkippedAssets.as_view(), name="skipped"),
    path(
        "files/sample_import_file/",
        SampleImportFile.as_view(),
        name="sample-import-file",
    ),
    path("filter-values/", AvailableFilterValues.as_view(), name="available-filters"),
]
if settings.DEBUG:
    urlpatterns += [
        path(
            "docs/",
            schema_view.with_ui("redoc", cache_timeout=None),
            name="schema-redoc",
        ),
        path(
            "docs/live/",
            schema_view.with_ui("swagger", cache_timeout=None),
            name="schema-swagger",
        ),
    ]

urlpatterns += router.urls
