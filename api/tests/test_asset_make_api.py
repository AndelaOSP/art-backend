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


class AssetMakeAPICase(APIBaseTestCase):
    def setUp(self):
        self.second_asset_make = {"name": "HP Envy", "asset_type": self.asset_type.id}

    def test_non_authenticated_user_view_assets_make_list(self):
        response = client.get(self.asset_make_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_assets_make(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.other_user.email}
        response = client.get(
            self.asset_make_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        data = response.data
        self.assertEqual(len(data["results"]), AssetMake.objects.count())
        self.assertIn(self.asset_make.name, list(data["results"][0].values()))
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_endpoint_post_invalid_data(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={"name": "", "asset_type": self.asset_type.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        # remove comment after deprecation of old fields
        # response_data = response.data
        # self.assertEqual(response_data['name'], ['This field may not be blank.'])

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
        response = client.post(
            self.asset_make_urls,
            data=self.second_asset_make,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        latest_asset_makes = AssetMake.objects.all()
        self.assertEqual(response.status_code, 201)
        response_data = response.data
        self.assertEqual(len(latest_asset_makes), initial_asset_makes + 1)
        self.assertIn(self.second_asset_make["name"].title(), response_data.values())

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_make_api_endpoint_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Test Edit", "asset_type": self.asset_type.id}
        response = client.put(
            "{}/{}/".format(self.asset_make_urls, self.asset_make.id),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get("name"), "Test Edit")

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_asset_make(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.asset_make_urls}/{self.asset_make.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertIn("name", response.data.keys())
        self.assertIn(self.asset_make.name, response.data.values())
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
    def test_asset_make_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.delete(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

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
        # I am always sure that Sades will be the last in the response
        #  since the Makes are ordered.
        self.assertEqual(3, len(response.data.get("results")))
        self.assertEqual(response.data.get("results")[2].get("name"), "Sades")
