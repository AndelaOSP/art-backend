# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import Asset, AssetLog, AssetModelNumber

User = get_user_model()
client = APIClient()


class AssetLogModelTest(APIBaseTestCase):
    """Tests for the AssetLog Model and API"""

    def setUp(self):
        self.test_assetmodel1 = AssetModelNumber.objects.create(
            model_number="IMN50987", make_label=self.make_label
        )

        self.test_other_asset = Asset(
            asset_code="IC00sf",
            serial_number="SN00134",
            model_number=self.test_assetmodel1,
            assigned_to=self.asset_assignee,
            purchase_date="2018-07-10",
        )
        self.test_other_asset.save()
        self.checkin = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type="Checkin"
        )
        self.checkout = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type="Checkout"
        )

    def test_add_checkin(self):
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type="Checkin",
        )
        self.assertEqual(AssetLog.objects.count(), 3)

    def test_add_checkout(self):
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type="Checkout",
        )
        self.assertEqual(AssetLog.objects.count(), 3)

    def test_add_checkin_without_log_type(self):
        with self.assertRaises(ValidationError) as e:
            AssetLog.objects.create(
                checked_by=self.security_user, asset=self.test_other_asset
            )

        self.assertEqual(
            e.exception.message_dict,
            {
                'log_type': ['This field cannot be blank.'],
                '__all__': ['Log type is required.'],
            },
        )

    def test_delete_checkin(self):
        self.assertEqual(AssetLog.objects.count(), 2)
        self.checkin.delete()
        self.assertEqual(AssetLog.objects.count(), 1)

    def test_update_checkin(self):
        self.checkin.asset = self.test_other_asset
        self.checkin.save()
        self.assertEqual(
            self.checkin.asset.asset_code, self.test_other_asset.asset_code
        )

    def test_update_checkout(self):
        self.checkout.asset = self.test_other_asset
        self.checkout.save()
        self.assertEqual(
            self.checkout.asset.asset_code, self.test_other_asset.asset_code
        )

    def test_non_authenticated_user_checkin_checkout(self):
        response = client.get(self.asset_logs_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    def test_checkout_model_string_representation(self):
        self.assertEqual(
            str(self.checkin.asset.serial_number), self.asset.serial_number
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_normal_user_list_checkin_checkout(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_logs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'},
        )
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_list_checkin_checkout(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.get(
            self.asset_logs_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertIn(self.checkout.id, response.data['results'][0].values())
        self.assertEqual(len(response.data['results']), AssetLog.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_user_list_checkin_checkout(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.asset_logs_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn(self.checkout.id, response.data['results'][0].values())
        self.assertEqual(len(response.data['results']), AssetLog.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_normal_user_create_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_logs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'},
        )
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {'asset': self.test_other_asset.id, 'log_type': 'Checkin'}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data['asset'],
            f"{self.test_other_asset.serial_number} - "
            f"{self.test_other_asset.asset_code}",
        )
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkout(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {'asset': self.test_other_asset.id, 'log_type': 'Checkout'}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data['asset'],
            f"{self.test_other_asset.serial_number} - "
            f"{self.test_other_asset.asset_code}",
        )
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_with_invalid_log_type(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        log_type = "Invalid"
        data = {'asset': self.test_other_asset.id, 'log_type': log_type}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data,
            {'log_type': ['"{}" is not a valid choice.'.format(log_type)]},
        )
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkin_without_asset(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {'log_type': 'Checkin'}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertDictEqual(response.data, {'asset': ['This field is required.']})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_view_checkin_detail(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.get(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data['id'], self.checkin.id)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_delete_checkin(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {'detail': 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_put_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.put(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {'detail': 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_patch_checkin(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.patch(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {'detail': 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)
