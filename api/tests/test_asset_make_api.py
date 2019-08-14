# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetMake

User = get_user_model()
client = APIClient()


class Post_AssetMakeAPICase(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_endpoint_post_invalid_data(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={"name": "", "asset_type": self.asset_type.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["name"], ["This field may not be null."])

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_endpoint_post_invalid_asset_type(self, mock_verify_id_token):
        invalid_asset_type = 500
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={"name": "Huawei Honor", "asset_type": invalid_asset_type},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response_data = response.data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_data["asset_type"],
            ['Invalid pk "{0}" - object does not exist.'.format(invalid_asset_type)],
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_endpoint_post_blank_asset_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={"name": "Huawei Honor", "asset_type": ""},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response_data = response.data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["asset_type"], ["This field is required."])

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_endpoint_post_valid_data(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        initial_asset_makes = len(AssetMake.objects.all())
        second_asset_make = {"name": "HP Envy", "asset_type": self.asset_type.id}
        response = client.post(
            self.asset_make_urls,
            data=second_asset_make,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        latest_asset_makes = AssetMake.objects.all()
        self.assertEqual(response.status_code, 201)
        response_data = response.data
        self.assertEqual(len(latest_asset_makes), initial_asset_makes + 1)
        self.assertEqual(response.data["name"], second_asset_make["name"].title())
        self.assertEqual(response.data["asset_type"], self.asset_type.name)


class Get_AssetMakeAPICase(APIBaseTestCase):
    def test_non_authenticated_user_view_assets_make_list(self):
        response = client.get(self.asset_make_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_api_endpoint_orders_asset_make_by_make(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        AssetMake.objects.create(name="Sades", asset_type=self.asset_type)
        AssetMake.objects.create(name="Lenovo Charger", asset_type=self.asset_type)

        response = client.get(
            self.asset_make_urls, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(3, len(response.data.get("results")))
        self.assertEqual(response.data["results"][0]["name"], "Asset Makes")
        self.assertEqual(response.data["results"][1]["name"], "Lenovo Charger")
        self.assertEqual(response.data["results"][2]["name"], "Sades")
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_assets_make(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.other_user.email}
        response = client.get(
            self.asset_make_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        self.assertEqual(response.data["results"][0]["id"], self.asset_make.id)
        self.assertEqual(response.data["results"][0]["name"], self.asset_make.name)
        self.assertEqual(
            response.data["results"][0]["asset_type"], self.asset_make.asset_type.name
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_assets_make_by_valid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.other_user.email}
        response = client.get(
            "{}/{}/".format(self.asset_make_urls, self.asset_make.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        self.assertEqual(response.data["id"], self.asset_make.id)
        self.assertEqual(response.data["name"], self.asset_make.name)
        self.assertEqual(response.data["asset_type"], self.asset_make.asset_type.name)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_view_assets_make_by_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}/{}/".format(self.asset_make_urls, 300),
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Edit_AssetMakeAPICase(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_api_endpoint_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Test Edit", "asset_type": self.asset_type.id}
        response = client.put(
            "{}/{}/".format(self.asset_make_urls, self.asset_make.id),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["id"], self.asset_make.id)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["asset_type"], self.asset_type.name)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.patch(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_edit_asset_make_by_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test Edit", "asset_type": self.asset_type.id}
        response = client.put(
            "{}/{}/".format(self.asset_make_urls, 100),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class delete_AssetMakeAPICase(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_api_endpoint_can_delete_asset_make_with_valid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        second_asset_make = {"name": "mac book pro", "asset_type": self.asset_type.id}
        response = client.post(
            self.asset_make_urls,
            data=second_asset_make,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response = client.delete(
            "{}/{}/".format(self.asset_make_urls, response.data["id"]),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_delete_assets_make_by_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_make_urls, 300),
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
