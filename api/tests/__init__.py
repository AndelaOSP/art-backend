# Standard Library
import logging
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse

# App Imports
from core.slack_bot import SlackIntegration

logging.disable(logging.WARNING)

User = get_user_model()


class APIBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ais_api_endpoint = "http://ais_api.example.com"
        cls.ais_users_endpoint = cls.ais_api_endpoint + "/users"
        cls.env_vars = {
            "SLACK_TOKEN": "testtoken",
            "SLACK_LIMIT": "100",
            "AIS_LIMIT": "100",
            "AIS_URL": cls.ais_api_endpoint,
            "AIS_TOKEN": "testtoken",
            "RETRY_TIMEOUT": "1",
            "RETRIES": "4",
            "PROJECT_ID": "",
            "PRIVATE_KEY": "",
            "CLIENT_EMAIL": "",
        }
        # slack calls patch
        cls.patch_slack_id = patch.object(SlackIntegration, "get_user_slack_id")
        cls.patch_send_message = patch.object(SlackIntegration, "send_message")
        cls.patch_firebase = patch("api.authentication.auth")
        cls.patch_env = patch.dict("os.environ", cls.env_vars)

        cls.patch_slack_id.return_value = "test_id"
        cls.patch_send_message.return_value = ""
        cls.patch_slack_id.start()
        cls.patch_send_message.start()

        cls.patch_firebase.start()
        cls.patch_env.start()

        # locations
        cls.country = apps.get_model("core", "Country").objects.create(name="Kenya")
        cls.centre = apps.get_model("core", "AndelaCentre").objects.create(
            name="Dojo", country=cls.country
        )
        cls.department = apps.get_model("core", "Department").objects.create(
            name="Finance"
        )
        cls.department_travel = apps.get_model("core", "Department").objects.create(
            name="Travel"
        )

        cls.office_block = apps.get_model("core", "OfficeBlock").objects.create(
            name="Epic", location=cls.centre
        )
        cls.other_centre = apps.get_model("core", "AndelaCentre").objects.create(
            id=80, name="Epic", country=cls.country
        )
        cls.office_block_2 = apps.get_model("core", "OfficeBlock").objects.create(
            name="ET", location=cls.other_centre
        )
        cls.office_floor = apps.get_model("core", "OfficeFloor").objects.create(
            number=7, block=cls.office_block
        )
        cls.floor_section = apps.get_model("core", "OfficeFloorSection").objects.create(
            name="The Big Apple", floor=cls.office_floor
        )
        cls.office_workspace = apps.get_model("core", "OfficeWorkspace").objects.create(
            name="Yaba", section=cls.floor_section
        )

        # users
        cls.user = User.objects.create(
            email="test@andela.com",
            cohort=20,
            password="devpassword",
            location=cls.centre,
            department=cls.department,
        )
        cls.token_user = "testtoken"
        cls.admin_user = User.objects.create_superuser(
            email="admin@andela.com",
            cohort=20,
            password="devpassword",
            location=cls.centre,
            department=cls.department,
        )
        cls.token_admin = "admintesttoken"
        cls.other_user = User.objects.create_user(
            email="user1@andela.com",
            cohort=2,
            password="devpassword",
            location=cls.centre,
            department=cls.department,
        )
        cls.token_other_user = "otherusertesttoken"

        cls.normal_admin = User.objects.create_user(
            email="normaladmin@andela.com",
            cohort=2,
            password="devpassword123",
            is_staff=True,
            is_superuser=False,
            location=cls.centre,
            department=cls.department,
        )
        cls.test_normaladmin = "normaladmintoken"

        cls.security_user = User.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            location=cls.centre,
            department=cls.department,
            is_securityuser=True,
        )
        cls.token_checked_by = "securityusertoken"

        # assets
        cls.asset_category = apps.get_model("core", "AssetCategory").objects.create(
            name="Accessoriesssss"
        )

        cls.asset_sub_category = apps.get_model(
            "core", "AssetSubCategory"
        ).objects.create(
            name="Sub Category nameseses", asset_category=cls.asset_category
        )
        cls.asset_type = apps.get_model("core", "AssetType").objects.create(
            name="Asset Types", asset_sub_category=cls.asset_sub_category
        )
        cls.test_asset_type = apps.get_model("core", "AssetType").objects.create(
            name="Other Asset Types", asset_sub_category=cls.asset_sub_category
        )
        cls.asset_make = apps.get_model("core", "AssetMake").objects.create(
            name="Asset Makes", asset_type=cls.asset_type
        )
        cls.assetmodel = apps.get_model("core", "AssetModelNumber").objects.create(
            name="IMN50987345", asset_make=cls.asset_make
        )
        cls.asset = apps.get_model("core", "Asset").objects.create(
            asset_code="IC001455",
            serial_number="SN00123455",
            purchase_date="2018-07-10",
            model_number=cls.assetmodel,
            asset_location=cls.centre,
            department=cls.department,
        )
        cls.asset_1 = apps.get_model("core", "Asset").objects.create(
            asset_code="IC001456",
            serial_number="SN00123456",
            purchase_date="2018-07-10",
            model_number=cls.assetmodel,
            asset_location=cls.centre,
            department=cls.department,
        )
        cls.asset_assignee_department = apps.get_model(
            "core", "AssetAssignee"
        ).objects.get(department=cls.department_travel)
        cls.asset_assignee = apps.get_model("core", "AssetAssignee").objects.get(
            user=cls.user
        )
        cls.asset_2 = apps.get_model("core", "Asset").objects.create(
            asset_code="I0014567890",
            serial_number="SN01234567890",
            purchase_date="2019-01-10",
            model_number=cls.assetmodel,
            asset_location=cls.centre,
            department=cls.department,
        )

        cls.asset_3 = apps.get_model("core", "Asset").objects.create(
            asset_code="I0014567830",
            serial_number="SN01234567871",
            purchase_date="2019-01-10",
            model_number=cls.assetmodel,
            asset_location=cls.centre,
            department=cls.department,
        )

        cls.asset_assignee = apps.get_model("core", "AssetAssignee").objects.get(
            user=cls.user
        )
        cls.asset_condition = apps.get_model("core", "AssetCondition").objects.create(
            asset=cls.asset, notes="working"
        )
        cls.incident_report = apps.get_model(
            "core", "AssetIncidentReport"
        ).objects.create(
            asset=cls.asset,
            incident_type="Damaged",
            incident_location="44",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="John Doe",
            police_abstract_obtained="Yes",
        )
        cls.asset_specs = apps.get_model("core", "AssetSpecs").objects.create(
            screen_size=15,
            year_of_manufacture=2017,
            processor_speed=3.0,
            processor_type="Intel core i7",
            memory=8,
            storage=512,
        )
        cls.asset_status = apps.get_model("core", "AssetStatus").objects.get(
            asset=cls.asset
        )
        cls.report_status = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=cls.incident_report
        )

        # urls
        cls.allocations_urls = reverse("allocations-list")
        cls.asset_assignee_url = reverse("asset-assignee-list")
        cls.asset_condition_urls = reverse("asset-condition-list")
        cls.asset_health_urls = reverse("asset-health-list")
        cls.asset_logs_url = reverse("asset-logs-list")
        cls.asset_make_urls = reverse("asset-makes-list")
        cls.asset_model_no_url = reverse("asset-models-list")
        cls.asset_specs_url = reverse("asset-specs-list")
        cls.asset_status_urls = reverse("asset-status-list")
        cls.asset_sub_category_url = reverse("asset-sub-categories-list")
        cls.asset_type_url = reverse("asset-types-list")
        cls.asset_uploads_url = reverse("import-assets")
        cls.asset_urls = reverse("assets-list")
        cls.category_url = reverse("asset-categories-list")
        cls.centre_url = reverse("andela-centres-list")
        cls.country_url = reverse("countries-list")
        cls.department_url = reverse("departments-list")
        cls.feedback_url = reverse("user-feedback-list")
        cls.filter_values_urls = reverse("available-filters")
        cls.floor_number_url = reverse("office-floors-list")
        cls.floor_section_url = reverse("floor-sections-list")
        cls.incident_report_url = reverse("incidence-reports-list")
        cls.incident_report_status_url = reverse(
            "state-transitions-detail", kwargs={"pk": str(cls.report_status.id)}
        )
        cls.manage_asset_urls = reverse("manage-assets-list")
        cls.office_block_url = reverse("office-blocks-list")
        cls.office_workspace_url = reverse("office-workspaces-list")
        cls.security_users_admin_url = reverse("security-users-list")
        cls.users_url = reverse("users-list")
        cls.print_asset_url = reverse("export-assets")
        cls.center_block_url = reverse(
            "andela-centres-office-blocks", kwargs={"pk": str(cls.centre.id)}
        )
        cls.other_center_block_url = reverse(
            "andela-centres-office-blocks", kwargs={"pk": str(cls.other_centre.id)}
        )
        cls.downloads_url = reverse("download-files")
        cls.history_url = reverse("history-list")
        cls.assets_url = reverse("assets")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.patch_slack_id.stop()
        cls.patch_send_message.stop()
        cls.patch_firebase.stop()
        cls.patch_env.stop()
