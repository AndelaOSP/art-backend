# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core import constants
from core.models import Asset

User = get_user_model()
client = APIClient()


class AssetStatusAPITest(APIBaseTestCase):
    """Tests for the Asset Status API"""

    def test_non_authenticated_user_view_asset_status(self):
        response = client.get(self.asset_status_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            f"{self.asset.asset_code} - {self.asset.serial_number}",
            str(response.data["results"]),
        )
        self.assertEqual(len(response.data["results"]), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_single_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_status_urls, self.asset_status.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            f"{self.asset.asset_code} - {self.asset.serial_number}",
            response.data.values(),
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "current_status": "Available"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            f"{self.asset.asset_code} - {self.asset.serial_number}",
            response.data.values(),
        )

        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_invalid_serial_number(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": 100_000, "current_status": "Available"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"asset": ['Invalid pk "100000" - object does not exist.']}
        )

        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_invalid_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "current_status": "Invalid"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"current_status": ['"Invalid" is not a valid choice.']}
        )

        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_empty_payload(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"asset": ["This field is required."]})

        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_put_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.put(
            "{}/{}/".format(self.asset_status_urls, self.asset_status.id),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_patch_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.patch(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_delete_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)


class TestTransitionStateUpdateFromAssetStatusAPIModification(APIBaseTestCase):
    """
    Test Transition state modification when asset status changes from API modification
    """

    def setUp(self):
        self.incident_report = apps.get_model(
            "core", "AssetIncidentReport"
        ).objects.create(asset=self.asset)

    def allocate_asset(self):
        """
        Allocate asset to update status to allocated
        :return:
        """
        data = {"asset": self.asset.id, "current_assignee": self.asset_assignee.id}
        response = client.post(
            self.allocations_urls,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def get_transition_state(self):
        url = reverse(
            "state-transitions-detail", kwargs={"pk": str(self.incident_report.id)}
        )
        print(url)
        response = client.get(
            f"{url}/", HTTP_AUTHORIZATION="Token {}".format(self.admin_user)
        )
        return response.json()

    @patch("api.authentication.auth.verify_id_token")
    def test_update_asset_status_from_allocated_to_lost(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        self.allocate_asset()
        data = {"asset": self.asset.id, "current_status": constants.LOST}
        client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    @patch("api.authentication.auth.verify_id_token")
    def test_update_asset_status_from_allocated_to_damaged(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        self.allocate_asset()
        data = {"asset": self.asset.id, "current_status": constants.DAMAGED}
        client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    @patch("api.authentication.auth.verify_id_token")
    def test_update_asset_status_from_allocated_to_available(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        self.allocate_asset()
        data = {"asset": self.asset.id, "current_status": constants.AVAILABLE}
        client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)
