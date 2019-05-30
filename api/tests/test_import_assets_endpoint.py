# Standard Library
import os
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import Asset, AssetModelNumber

User = get_user_model()
client = APIClient()


class AssetsUploadTestCase(APIBaseTestCase):
    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.asset_uploads_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_can_upload_csv_file_to_save_assets(
        self, mock_verify_id_token
    ):

        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(os.path.dirname(__file__), "sample.csv")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )
        skipped_filename = f"{response.data['filename']}.csv"
        self.assertGreater(Asset.objects.count(), count)
        self.assertEqual(200, response.status_code)

        filename = "{}.csv".format(self.admin_user.email.split("@")[0])

        self.assertEqual(skipped_filename, filename)

    @patch("api.authentication.auth.verify_id_token")
    def test_upload_csv_file_with_minimum_required_fields(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        AssetModelNumber.objects.create(name="HP 27ES", asset_make=self.asset_make)
        file_location = os.path.join(os.path.dirname(__file__), "sample_limited.csv")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )

        self.assertGreater(Asset.objects.count(), count)
        self.assertEqual(200, response.status_code)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_upload_empty_csv_file_to_save_assets(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(os.path.dirname(__file__), "empty_csv.csv")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )

        self.assertEqual(Asset.objects.count(), count)
        self.assertEqual(400, response.status_code)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_upload_csv_file_containing_only_headings_to_save_assets(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(os.path.dirname(__file__), "heading_csv.csv")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )

        self.assertEqual(Asset.objects.count(), count)
        self.assertEqual(400, response.status_code)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_upload_non_csv_file_type_to_save_assets(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(os.path.dirname(__file__), "text_file.txt")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )

        self.assertEqual(Asset.objects.count(), count)
        self.assertEqual(400, response.status_code)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_upload_csv_file_with_missing_required_headings_to_save_assets(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(os.path.dirname(__file__), "missing_headings.csv")
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )

        self.assertEqual(Asset.objects.count(), count)
        self.assertEqual(400, response.status_code)

    @patch("api.authentication.auth.verify_id_token")
    def test_uploading_assets_already_in_the_database_skips_saving_them(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        count = Asset.objects.count()
        file_location = os.path.join(
            os.path.dirname(__file__), "sample_with_duplicates.csv"
        )
        with open(file_location) as csv:
            data["file"] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
            )
        self.assertIn("fail", response.data)
        self.assertEqual(Asset.objects.count(), count + 1)
