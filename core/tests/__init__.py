# Standard Library
import logging
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from django.test import TestCase

# App Imports
from core.slack_bot import SlackIntegration

logging.disable(logging.WARNING)


class CoreBaseTestCase(TestCase):
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
        cls.patch_slack_id = patch.object(SlackIntegration, "get_user_slack_id")
        cls.patch_send_message = patch.object(SlackIntegration, "send_message")
        cls.patch_firebase = patch("api.authentication.auth")
        cls.patch_env = patch.dict("os.environ", cls.env_vars)

        cls.patch_firebase.start()

        cls.patch_slack_id.return_value = "test_id"
        cls.patch_send_message.return_value = ""
        cls.patch_slack_id.start()
        cls.patch_send_message.start()
        cls.patch_env.start()

        cls.user = apps.get_model("core", "User").objects.create(
            email="test@andela.com", cohort=10, password="devpassword"
        )
        cls.asset_assignee = apps.get_model("core", "AssetAssignee").objects.get(
            user=cls.user
        )

        cls.user2 = apps.get_model("core", "User").objects.create(
            email="test15@andela.com", cohort=15, password="devpassword"
        )
        cls.asset_assignee2 = apps.get_model("core", "AssetAssignee").objects.get(
            user=cls.user2
        )

        cls.security_user = apps.get_model("core", "User").objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            is_securityuser=True,
        )

        cls.category = apps.get_model("core", "AssetCategory").objects.create(
            name="Computer"
        )
        cls.asset_sub_category = apps.get_model(
            "core", "AssetSubCategory"
        ).objects.create(name="Computer Accessories", asset_category=cls.category)
        cls.asset_type = apps.get_model("core", "AssetType").objects.create(
            name="Accessory", asset_sub_category=cls.asset_sub_category
        )
        cls.asset_make = apps.get_model("core", "AssetMake").objects.create(
            name="Sades", asset_type=cls.asset_type
        )
        cls.test_assetmodel = apps.get_model("core", "AssetModelNumber").objects.create(
            name="12345", asset_make=cls.asset_make
        )

        cls.test_asset = apps.get_model("core", "Asset").objects.create(
            asset_code="IC001",
            serial_number="SN001",
            model_number=cls.test_assetmodel,
            purchase_date="2018-07-10",
        )

        cls.test_asset_1 = apps.get_model("core", "Asset").objects.create(
            asset_code="IC003",
            serial_number="SN003",
            model_number=cls.test_assetmodel,
            purchase_date="2018-07-10",
        )

        cls.test_asset_2 = apps.get_model("core", "Asset").objects.create(
            asset_code="IC002",
            serial_number="SN002",
            model_number=cls.test_assetmodel,
            purchase_date="2018-07-10",
        )
        cls.country = apps.get_model("core", "Country").objects.create(name="Nigeria")
        cls.centre = apps.get_model("core", "AndelaCentre").objects.create(
            name="ET", country=cls.country
        )
        cls.office_block = apps.get_model("core", "OfficeBlock").objects.create(
            name="Andela Tower", location=cls.centre
        )
        cls.office_floor = apps.get_model("core", "OfficeFloor").objects.create(
            block=cls.office_block, number=14
        )
        cls.office_section = apps.get_model(
            "core", "OfficeFloorSection"
        ).objects.create(name="Safari", floor=cls.office_floor)
        cls.office_workspace = apps.get_model("core", "OfficeWorkspace").objects.create(
            name="DeveloperA Workspace", section=cls.office_section
        )
        cls.department = apps.get_model("core", "Department").objects.create(
            name="Finance"
        )
        apps.get_model("core", "AllocationHistory").objects.create(
            asset=cls.test_asset_1, current_assignee=cls.user.assetassignee
        )
        apps.get_model("core", "AssetSpecs").objects.create()
        apps.get_model("core", "AssetCondition").objects.create(
            asset=cls.test_asset_1, notes="test"
        )
        apps.get_model("core", "AssetIncidentReport").objects.create(
            asset=cls.test_asset_1
        )
        apps.get_model("core", "AISUserSync").objects.create()
        apps.get_model("core", "UserFeedback").objects.create(
            reported_by=cls.user, message="This is feedback", report_type="feedback"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.patch_slack_id.stop()
        cls.patch_send_message.stop()
        cls.patch_firebase.stop()
        cls.patch_env.stop()
