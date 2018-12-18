from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from api.tests import APIBaseTestCase
from core.models import Asset, AssetLog, AllocationHistory, AssetStatus, AndelaCentre

User = get_user_model()
client = APIClient()


class ManageAssetTestCase(APIBaseTestCase):
    def setUp(self):
        self.data = {
            "asset_code": "IC003",
            "serial_number": "SN003",
            "model_number": self.assetmodel.model_number}

    def test_non_authenticated_admin_view_assets(self):
        response = client.get(self.manage_asset_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_view_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset.asset_code, str(response.data['results']))
        self.assertEqual(len(response.data['results']), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_view_assets_in_their_centres_only(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        location = AndelaCentre.objects.create(
            centre_name="Kitale", country="Uganda"
        )
        Asset.objects.create(
            asset_code="IC001457", serial_number="SN00123457",
            purchase_date="2018-07-10", model_number=self.assetmodel, asset_location=location
        )
        response = client.get(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset.asset_code, str(response.data['results']))
        self.assertEqual(len(response.data['results']), Asset.objects.count() - 1)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_cannot_view_all_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_cannot_post_put_or_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.post(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 403)

        response = client.put(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 403)

        response = client.delete(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_view_all_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.manage_asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(len(response.data['results']), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_post_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_code": "IC002",
            "serial_number": "SN002",
            "model_number": self.assetmodel.model_number,
            "purchase_date": "2018-07-10"
        }
        count = Asset.objects.count()
        response = client.post(
            self.manage_asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        res_data = response.data
        self.assertEqual(
            data.get("asset_code"), res_data.get("asset_code"))
        self.assertEqual(
            data.get("serial_number"), res_data.get("serial_number"))
        self.assertEqual(
            data.get("model_number"), res_data.get("model_number"))
        self.assertEqual(Asset.objects.count(), count + 1)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_post_asset_with_specs(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_code": "IC003",
            "serial_number": "SN003",
            "model_number": self.assetmodel.model_number,
            "purchase_date": "2018-07-10",
            "processor_type": "Intel core i3",
            "processor_speed": 2.3,
            "screen_size": 15
        }
        response = client.post(
            self.manage_asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        res_data = response.data
        self.assertEqual(
            data.get("serial_number"), res_data.get("serial_number"))
        self.assertIsNotNone(res_data.get('specs', None))
        self.assertEqual(
            data['screen_size'],
            res_data.get('specs').get('screen_size'))
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_cannot_post_asset_with_invalid_specs_fields(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_code": "IC002",
            "serial_number": "SN002",
            "model_number": self.assetmodel.model_number,
            "purchase_date": "2018-07-10",
            "processor_type": "Intel core i3",
            "processor_speed": 5.0,
            "screen_size": 19
        }

        response = client.post(
            self.manage_asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 400)
        self.assertIn("screen_size", response.data)
        self.assertIn("processor_speed", response.data)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_cannot_post_asset_with_missing_fields(
            self,
            mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "model_number": self.assetmodel.model_number,
            "purchase_date": "2018-07-10"
        }

        response = client.post(
            self.manage_asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['asset_code'], ['This field is required.'])
        self.assertEqual(response.data['serial_number'], ['This field is required.'])

    @patch('api.authentication.auth.verify_id_token')
    def test_cannot_post_asset_with_invalid_model_number(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}

        self.assetmodel.id = 300

        data = {
            "asset_code": "IC002",
            "serial_number": "SN002",
            "model_number": self.assetmodel.id,
            "purchase_date": "2018-07-10"
        }
        response = client.post(
            self.manage_asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'model_number': ['Object with model_number=300 does not exist.']
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.patch(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_detail_api_endpoint_contain_assigned_to_details(self, mock_verify_id_token):
        AssetStatus.objects.create(asset=self.asset, current_status='Available')
        AllocationHistory.objects.create(asset=self.asset, current_owner=self.user.assetassignee)
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.user.email, response.data['assigned_to'].values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_assigned_to_details_has_no_password(self, mock_verify_id_token):
        AllocationHistory.objects.create(asset=self.asset_1, current_owner=self.user.assetassignee)
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset_1.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertNotIn('password', response.data['assigned_to'].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_non_checked_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'], None)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checked_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.asset,
            log_type="Checkin"
        )

        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_in")
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checkout_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.asset,
            log_type="Checkout"
        )
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_out")
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_in_asset_api(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('asset_type', response.data.keys())
        self.assertEqual(response.data['asset_type'],
                         self.asset_type.asset_type)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_by_email(self, mock_verify_id_token):
        AllocationHistory.objects.create(asset=self.asset, current_owner=self.user.assetassignee)
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?email={}'.format(self.manage_asset_urls, self.user.email),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.user.email,
                      response.data['results'][0]['assigned_to']['email'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_non_existing_email_return_empty(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?email={}'.format(self.manage_asset_urls,
                                 'userwithnoasset@site.com'),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertFalse(len(response.data['results']) > 0)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_by_asset_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?asset_type={}'.format(self.manage_asset_urls, self.asset_type.asset_type),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertIn(self.asset_type.asset_type,
                      response.data['results'][0]['asset_type'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_by_invalid_asset_type_return_no_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?asset_type={}'.format(self.manage_asset_urls, 'InvalidAssetType'),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data['count'], 0)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_by_model_number(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?model_number={}'.format(self.manage_asset_urls, self.assetmodel.model_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertIn(self.assetmodel.model_number,
                      response.data['results'][0]['model_number'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_filter_by_invalid_model_number_return_no_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?model_number={}'.format(self.manage_asset_urls, 'InvalidModelNumber'),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data['count'], 0)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_have_allocation_history(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                              HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('allocation_history', response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_update_assets_location(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = self.data
        data['asset_location'] = "Nairobi"
        AndelaCentre.objects.create(
            centre_name="Nairobi",
            country="Kenya")
        res = client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                         HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(res.data.get('asset_location'), "Dojo")
        client.put(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid), data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        response = client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                              HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(response.data.get('asset_location'), "Nairobi")

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_cannot_update_assets_to_no_existing_location(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_code": "IC003",
            "serial_number": "SN003",
            "asset_location": "Mombasa",
            "model_number": self.assetmodel.model_number}
        AndelaCentre.objects.create(
            centre_name="Nairobi",
            country="Kenya")
        res = client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                         HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertNotEqual(res.data.get('asset_location'), "Nairobi")
        res = client.put(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid), data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(res.status_code, 400)
        response = client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                              HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertNotEqual(response.data.get('asset_location'), "Nairobi")

    @patch('api.authentication.auth.verify_id_token')
    def test_non_superuser_can_not_update_an_asset_location(self, mock_verify_id_token):
        user = User.objects.create_user(
            email='adminuser@site.com', cohort=20,
            slack_handle='@adminu', password='devpassword', is_staff=True, is_superuser=False
        )
        mock_verify_id_token.return_value = {'email': user.email}
        data = self.data
        data['asset_location'] = "Nairobi"
        AndelaCentre.objects.create(centre_name="Nairobi", country="Kenya")
        res = client.put(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid), data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(res.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_a_superuser_can_update_an_asset_location(self, mock_verify_id_token):
        admin = User.objects.create_user(
            email='adminadmin@site.com', cohort=20,
            slack_handle='@adminsuper', password='devpassword', is_staff=True, is_superuser=True
        )
        mock_verify_id_token.return_value = {'email': admin.email}

        AndelaCentre.objects.create(centre_name="Nairobi", country="Kenya")
        data = self.data
        data['asset_location'] = "Nairobi"

        res = client.put(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid), data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(res.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_update_asset_verification_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = self.data
        data['verified'] = False
        get = self.client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                              HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertTrue(get.data.get('verified'))
        res = client.put(
            '{}/{}/'.format(self.manage_asset_urls, self.asset.uuid), data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(res.status_code, 200)
        response = self.client.get('{}/{}/'.format(self.manage_asset_urls, self.asset.uuid),
                                   HTTP_AUTHORIZATION="Token {}".format(self.token_admin))

        self.assertFalse(response.data.get('verified'))
