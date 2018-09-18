from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, AssetCategory, AssetSubCategory, \
    AssetType, AssetMake, AssetModelNumber

from api.tests import APIBaseTestCase

client = APIClient()


class AssetModelNumberAPITest(APIBaseTestCase):
    ''' Tests for the Asset Model Number endpoint'''

    def setUp(self):
        super(AssetModelNumberAPITest, self).setUp()
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.asset_category = AssetCategory.objects.create(
            category_name='Accessories'
        )
        self.asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name='Key Board',
            asset_category=self.asset_category
        )
        self.asset_type = AssetType.objects.create(
            asset_type='Dell',
            asset_sub_category=self.asset_sub_category
        )

        self.asset_label = AssetMake.objects.create(
            make_label='ASSET-LABEL',
            asset_type=self.asset_type
        )

        self.asset_model_no = AssetModelNumber.objects.create(
            model_number='TEST-MODEL-NO',
            make_label=self.asset_label
        )

        self.asset_model_no_url = reverse('asset-models-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_asset_model_number(self):
        response = client.get(self.asset_model_no_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_asset_model_number(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            'model_number': 'TEST-MODEL-NO-1',
            'make_label': self.asset_label.id
        }
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertIn('model_number', response.data.keys())
        self.assertIn(data['model_number'], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_asset_model_numbers(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_model_no_url,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))

        self.assertEqual(len(response.data['results']),
                         AssetCategory.objects.count())
        self.assertIn('model_number', response.data['results'][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_asset_model_number(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            f'{self.asset_model_no_url}/{self.asset_model_no.id}/',
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))

        self.assertIn('model_number', response.data.keys())
        self.assertIn(self.asset_model_no.model_number,
                      response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_model_number_api_endpoint_cant_allow_put(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.put(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_model_number_api_endpoint_cant_allow_patch(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.patch(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_model_number_api_endpoint_cant_allow_delete(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_cannot_post_empty_model_number(
            self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            'model_number': '',
            'make_label': self.asset_label.id
        }
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEquals(response.data, {
            'model_number': ['This field may not be blank.']})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_cannot_post_invalid_make_label(
            self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            'model_number': 'TEST',
            'make_label': 'Invalid'
        }
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEquals(response.data, {
            'make_label': [
                f'Invalid pk "{data["make_label"]}" - object does not exist.'
            ]})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_cannot_post_empty_make_label(
            self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            'model_number': 'TEST',
            'make_label': ''
        }
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEquals(response.data, {
            'make_label': ['This field is required.']})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_model_number_api_orders_asset_models_by_model_number(self,
                                                                        mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        AssetModelNumber.objects.create(
            model_number='BCD6G4D6 1F',
            make_label=self.asset_label
        )
        AssetModelNumber.objects.create(
            model_number='XD6GRD6 Q3',
            make_label=self.asset_label
        )

        response = client.get(
            self.asset_model_no_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        # I am always sure that 'XD6GRD6 Q3' will be the last in the response
        #  since the model numbers are ordered.
        self.assertEqual(3, len(response.data.get('results')))
        self.assertEqual(response.data.get('results')[2].get('model_number'), "XD6GRD6 Q3")
