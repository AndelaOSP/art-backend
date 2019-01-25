# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class DeprecationTestCase(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_category(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        category = client.get(
            f"{self.category_url}/{self.asset_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", category.data.keys())
        self.assertIn("category_name", category.data.keys())
        self.assertEqual(category.data.get("name"), category.data.get("category_name"))

        # post
        data = {"category_name": "depr computer"}
        response = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_sub_category(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        sub_category = client.get(
            f"{self.asset_sub_category_url}/{self.asset_sub_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", sub_category.data.keys())
        self.assertIn("sub_category_name", sub_category.data.keys())
        self.assertEqual(
            sub_category.data.get("name"), sub_category.data.get("sub_category_name")
        )

        # post
        data = {
            "sub_category_name": "Monitor",
            "asset_category": self.asset_category.id,
        }
        response = client.post(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_make(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        make = client.get(
            f"{self.asset_make_urls}/{self.asset_make.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", make.data.keys())
        self.assertIn("make_label", make.data.keys())
        self.assertEqual(make.data.get("name"), make.data.get("make_label"))

        # post
        data = {"make_label": "HP Envy", "asset_type": self.asset_type.id}
        response = client.post(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_model_number(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        model_number = client.get(
            f"{self.asset_model_no_url}/{self.assetmodel.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", model_number.data.keys())
        self.assertIn("model_number", model_number.data.keys())
        self.assertIn("asset_make", model_number.data.keys())
        self.assertIn("make_label", model_number.data.keys())
        self.assertEqual(
            model_number.data.get("name"), model_number.data.get("model_number")
        )
        self.assertEqual(
            model_number.data.get("asset_make"), model_number.data.get("make_label")
        )

        # post
        data = {"model_number": "TEST-MODEL-NO-1", "make_label": self.asset_make.id}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_asset_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        asset_type = client.get(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", asset_type.data.keys())
        self.assertIn("asset_type", asset_type.data.keys())
        self.assertEqual(asset_type.data.get("name"), asset_type.data.get("asset_type"))

        # post
        data = {
            "asset_type": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id,
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_andela_centre(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        andela_centre = client.get(
            f"{self.centre_url}/{self.asset_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", andela_centre.data.keys())
        self.assertIn("centre_name", andela_centre.data.keys())
        self.assertEqual(
            andela_centre.data.get("name"), andela_centre.data.get("centre_name")
        )

        # post
        data = {"centre_name": "ET", "country": self.country.id}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_manage_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        # get
        asset = client.get(
            f"{self.manage_asset_urls}/{self.asset.uuid}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("asset_make", asset.data.keys())
        self.assertIn("make_label", asset.data.keys())
        self.assertEqual(asset.data.get("asset_make"), asset.data.get("make_label"))

    @patch("api.authentication.auth.verify_id_token")
    def test_deprecated_fields_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        # get
        asset = client.get(
            "{}?asset_code={}".format(self.asset_urls, self.asset.asset_code),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertIn("asset_make", asset.data["results"][0].keys())
        self.assertIn("make_label", asset.data["results"][0].keys())
        self.assertEqual(
            asset.data["results"][0].get("asset_make"),
            asset.data["results"][0].get("make_label"),
        )
