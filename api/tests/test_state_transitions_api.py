# Standard Library
from datetime import datetime
from unittest.mock import patch

# Third-Party Imports
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetIncidentReport, StateTransition

client = APIClient()


class StateTransitionAPITest(APIBaseTestCase):
    """ Tests for the AssetIncidentReport API """

    def setUp(self):
        self.transition_state = StateTransition(
            asset_incident_report=self.incident_report,
            incident_report_state="newly reported",
            asset_state_from_report="requires repair",
        )
        self.transition_state.save()


class Post_StateTransitionAPITest(StateTransitionAPITest):
    def test_non_authenticated_user_view_incident_report(self):
        response = client.get(self.incident_report_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {
            "asset_incident_report": self.incident_report.id,
            "incident_report_state": "internal assessment",
            "asset_state_from_report": "Damaged",
        }
        response = client.post(
            self.state_transitions_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data["asset_incident_report"], self.incident_report.id
        )
        self.assertEqual(
            response.data["incident_report_state"], data["incident_report_state"]
        )
        self.assertEqual(
            response.data["asset_state_from_report"], data["asset_state_from_report"]
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_post_invalid_asset_incident_report(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {
            "asset_incident_report": None,
            "incident_report_state": "concurrent",
            "asset_state_from_report": "beyond damaged",
        }
        response = client.post(
            self.state_transitions_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            str(response.data["asset_incident_report"][0]),
            "Incorrect type. Expected pk value, received str.",
        )
        self.assertEqual(
            str(response.data["incident_report_state"][0]),
            '"concurrent" is not a valid choice.',
        )
        self.assertEqual(
            str(response.data["asset_state_from_report"][0]),
            '"beyond damaged" is not a valid choice.',
        )
        self.assertEqual(response.status_code, 400)


class Get_StateTransitionAPITest(StateTransitionAPITest):
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_transaction_state_report(
        self, mock_verify_id_token
    ):

        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.state_transitions_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][1]["id"], self.transition_state.id)
        self.assertEqual(
            response.data["results"][1]["asset_incident_report"],
            self.transition_state.asset_incident_report.id,
        )
        self.assertEqual(
            response.data["results"][1]["incident_report_state"],
            self.transition_state.incident_report_state,
        )
        self.assertEqual(
            response.data["results"][1]["asset_state_from_report"],
            self.transition_state.asset_state_from_report,
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_single_transaction_state_report(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.state_transitions_url}/{self.transition_state.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.transition_state.id)
        self.assertEqual(
            response.data["asset_incident_report"],
            self.transition_state.asset_incident_report.id,
        )
        self.assertEqual(
            response.data["incident_report_state"],
            self.transition_state.incident_report_state,
        )
        self.assertEqual(
            response.data["asset_state_from_report"],
            self.transition_state.asset_state_from_report,
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_get_transaction_state_report_with_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.state_transitions_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Edit_StateTransitionAPITest(StateTransitionAPITest):
    @patch("api.authentication.auth.verify_id_token")
    def test_can_allow_edit_of_transaction_state_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {
            "asset_incident_report": self.incident_report.id,
            "incident_report_state": "external assessment",
            "asset_state_from_report": "Damaged",
        }
        response = client.put(
            f"{self.state_transitions_url}/{self.transition_state.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["id"], self.transition_state.id)
        self.assertEqual(
            response.data["asset_incident_report"], self.incident_report.id
        )
        self.assertEqual(
            response.data["incident_report_state"], data["incident_report_state"]
        )
        self.assertEqual(
            response.data["asset_state_from_report"], data["asset_state_from_report"]
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_edit_transaction_state_report_with_invalid_id(
        self, mock_verify_id_token
    ):
        data = {
            "asset_incident_report": self.incident_report.id,
            "incident_report_state": "external assessment",
            "asset_state_from_report": "Damaged",
        }
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.put(
            f"{self.state_transitions_url}/{300}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Delete_StateTransitionAPITest(StateTransitionAPITest):
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_delete_transaction_state_report_with_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.state_transitions_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_allow_delete_of_transaction_state_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.state_transitions_url}/{self.transition_state.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)
