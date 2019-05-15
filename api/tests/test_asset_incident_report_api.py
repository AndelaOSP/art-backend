# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetIncidentReport

client = APIClient()


class AssetIncidentReportAPITest(APIBaseTestCase):
    """ Tests for the AssetIncidentReport API """

    def test_non_authenticated_user_view_incident_report(self):
        response = client.get(self.incident_report_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {
            "asset": self.asset.id,
            "incident_type": "Loss",
            "incident_location": "CDB",
            "incident_description": "Lorem Ipsum",
            "injuries_sustained": "N/a",
            "loss_of_property": "Mobile Phone",
            "witnesses": "John Doe +2347548458457",
            "police_abstract_obtained": "Yes",
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            f"{self.asset.serial_number} - {self.asset.asset_code}",
            response.data.values(),
        )
        self.assertIn("submitted_by", response.data.keys())
        self.assertEqual(response.data["submitted_by"], self.user.email)
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_invalid_incident_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {
            "asset": self.asset.id,
            "incident_type": "Invalid",
            "incident_location": "CDB",
            "incident_description": "Lorem Ipsum",
            "injuries_sustained": "N/a",
            "loss_of_property": "Mobile Phone",
            "witnesses": "John Doe +2347548458457",
            "police_abstract_obtained": "Yes",
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"incident_type": ['"Invalid" is not a valid choice.']}
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_empty_incident_fields(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {
            "asset": self.asset.id,
            "incident_type": "Loss",
            "incident_location": "",
            "incident_description": "Lorem",
            "police_abstract_obtained": "Yes",
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"incident_location": ["This field may not be blank."]}
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(self.incident_report.id, response.data["results"][0].values())
        self.assertEqual(
            len(response.data["results"]), AssetIncidentReport.objects.count()
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_single_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.incident_report_url}/{self.incident_report.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(self.incident_report.id, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_allow_put_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.put(
            f"{self.incident_report_url}/{self.incident_report.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_allow_patch_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.patch(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_allow_delete_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_allow_patch_of_incident_report_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "incident_report_state": "internal assessment",
            "asset_state_from_report": "Damaged",
        }
        response = client.patch(
            f"{self.incident_report_status_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        data['id'] = self.report_status.id
        data['asset_incident_report'] = self.report_status.asset_incident_report.id
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_require_both_fields_to_patch_incident_report_status(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_incident_report": self.report_status.asset_incident_report.id,
            "incident_report_state": "internal assessment",
        }
        response = client.patch(
            f"{self.incident_report_status_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {
                "Error": "Ensure that incident_report_state and asset_state_from_report fields are filled"
            },
        )
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_restrict_patch_of_incident_report_status_for_external_assessment(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "incident_report_state": "external assessment",
            "asset_state_from_report": "requires external assessment",
        }
        response = client.patch(
            f"{self.incident_report_status_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {"Error": "Asset state option is not valid for given report state"},
        )
        self.assertEqual(response.status_code, 400)
