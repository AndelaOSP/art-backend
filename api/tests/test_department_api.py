# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class DepartmentAPITest(APIBaseTestCase):
    """ Tests for the Department endpoint"""

    def test_non_authenticated_user_get_departments(self):
        response = client.get(self.department_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_department(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "People"}
        response = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_post_department_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": self.department.name}
        response = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_editing_department(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "People"}
        res = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        department_url = reverse("departments-detail", args={res.data.get("id")})

        response = client.put(
            department_url,
            data={"name": "Facilities"},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {"name": "Facilities", "id": res.data.get("id"), "number_of_assets": 0},
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_getting_department(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        department_url = reverse("departments-detail", args={self.department.id})

        response = client.get(
            department_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data["name"], self.department.name)
        self.assertEqual(response.data["id"], self.department.id)
        self.assertEqual(response.data["assets_assigned"]["results"], [])
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_getting_department_with_assets(self, mock_verify_id_token):
        self.asset_2.assigned_to = self.asset_assignee_department
        self.asset_2.save()
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        department_url = reverse("departments-detail", args={self.department_travel.id})
        response = client.get(
            department_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["assets_assigned"]["results"][0]["asset_code"],
            self.asset_2.asset_code,
        )
        self.assertEqual(
            response.data["assets_assigned"]["results"][0]["serial_number"],
            self.asset_2.serial_number,
        )
        self.assertEqual(
            response.data["assets_assigned"]["results"][0]["asset_type"],
            self.asset_2.asset_type,
        )
        self.assertEqual(
            response.data["assets_assigned"]["results"][0]["uuid"],
            str(self.asset_2.uuid),
        )
        self.assertEqual(
            response.data["assets_assigned"]["results"][0]["asset_category"],
            self.asset_2.asset_category,
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_delete_department(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Big Success"}

        res = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        department_url = reverse("departments-detail", args={res.data.get("id")})

        response = client.delete(
            department_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data, {"detail": "Deleted Successfully"})
        self.assertEqual(response.status_code, 204)
