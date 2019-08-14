# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetType

client = APIClient()


class Post_AssetCategoryAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def test_non_authenticated_user_create_asset_type(self):
        data = {
            "name": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id,
        }
        response = client.post(
            self.asset_type_url,
            data=data
        )
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "name": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id,
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data['name'])
        self.assertEqual(response.data["asset_sub_category"], self.asset_sub_category.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_asset_type_with_empty_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "name": "",
            "asset_sub_category": self.asset_sub_category.id,
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["name"][0], 'This field may not be null.')

class Get_AssetCategoryAPITest(APIBaseTestCase):

    def test_non_authenticated_user_get_asset_asset_type(self):
        response = client.get(self.asset_type_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_asset_types(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.asset_type_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )

        self.assertEqual(len(response.data["results"]), AssetType.objects.count())
        self.assertEqual(response.data["results"][0]['name'],self.asset_type.name)
        self.assertEqual(response.data["results"][0]['id'],self.asset_type.id)
        self.assertEqual(response.data['results'][0]['asset_sub_category'],self.asset_sub_category.name)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )

        self.assertEqual(response.data['name'],self.asset_type.name)
        self.assertEqual(response.data['id'],self.asset_type.id)
        self.assertEqual(response.data['asset_sub_category'],self.asset_sub_category.name)
        self.assertEqual(response.status_code, 200)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_orders_asset_types_by_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetType.objects.create(name="HP", asset_sub_category=self.asset_sub_category)
        AssetType.objects.create(
            name="Samsung", asset_sub_category=self.asset_sub_category
        )
        AssetType.objects.create(
            name="Lenovo", asset_sub_category=self.asset_sub_category
        )

        response = client.get(
            self.asset_type_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(AssetType.objects.count(), len(response.data.get("results")))
        self.assertEqual(response.data.get("results")[-1].get("name"), "Samsung")

    
    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_asset_type_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_type_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Edit_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test Edit", "asset_sub_category": self.asset_sub_category.id}
        response = client.put(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data['name'],data["name"])
        self.assertEqual(response.data['id'],self.asset_type.id)
        self.assertEqual(response.data['asset_sub_category'],self.asset_sub_category.name)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_edit_single_asset_type_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test Edit", "asset_sub_category": self.asset_sub_category.id}
        response = client.put(
            f"{self.asset_type_url}/{90}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.patch(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

class Delete_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {
            "name": "Asset Type3",
            "asset_sub_category": self.asset_sub_category.id,
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        response = client.delete(
            f"{self.asset_type_url}/{response.data['id']}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 204)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_can_delete_single_asset_type_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.asset_type_url}/{50}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
