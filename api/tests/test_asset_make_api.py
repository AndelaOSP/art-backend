from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import (
                         AssetMake,
                         AssetType,
                         AssetSubCategory,
                         AssetCategory)

User = get_user_model()
client = APIClient()


class AssetMakeAPICase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_user = 'testtoken'
        self.other_user = User.objects.create_user(
            email='user1@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_other_user = 'otherusertesttoken'
        self.asset_category = AssetCategory.objects.create(
            category_name='Electronics')
        self.asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name='Computer',
            asset_category=self.asset_category)
        self.asset_type = AssetType.objects.create(
            asset_type='Laptop',
            asset_sub_category=self.asset_sub_category)
        self.asset_make = AssetMake.objects.create(
            make_label='MacBook Pro', asset_type=self.asset_type)
        self.second_asset_make = {
            'make_label': 'HP Envy',
            'asset_type': self.asset_type.id
        }

        self.invalid_asset_type = 500
        self.invalid_asset_make = '       '
        self.blank_asset_type = ''
        self.asset_make.save()
        self.asset_make_urls = reverse('asset-makes-list')

    def test_non_authenticated_user_view_assets_make_list(self):
        response = client.get(self.asset_make_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 401)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_view_assets_make(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            self.asset_make_urls,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_other_user))
        data = response.data
        self.assertEqual(len(data), AssetMake.objects.count())
        self.assertIn(self.asset_make.make_label, list(data[0].values()))
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_endpoint_post_invalid_data(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={'make_label': self.invalid_asset_make,
                  'asset_type': self.asset_type.id
                  },
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user)
        )
        response_data = response.data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['make_label'],
                         ['This field may not be blank.'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_endpoint_post_invalid_asset_type(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={'make_label': 'Huawei Honor',
                  'asset_type': self.invalid_asset_type
                  },
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user)
        )
        response_data = response.data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['asset_type'],
                         ['Invalid pk "{0}" - object does not exist.'
                         .format(self.invalid_asset_type)])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_endpoint_post_blank_asset_type(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.post(
            self.asset_make_urls,
            data={'make_label': 'Huawei Honor',
                  'asset_type': self.blank_asset_type
                  },
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user)
        )
        response_data = response.data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['asset_type'],
                         ['This field is required.'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_endpoint_post_valid_data(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        initial_asset_makes = len(AssetMake.objects.all())
        response = client.post(
            self.asset_make_urls,
            data=self.second_asset_make,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user)
        )
        latest_asset_makes = AssetMake.objects.all()
        self.assertEqual(response.status_code, 201)
        response_data = response.data
        self.assertEqual(len(latest_asset_makes), initial_asset_makes + 1)
        self.assertIn(self.second_asset_make['make_label'],
                      response_data.values())

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            '{}{}/'.format(self.asset_make_urls, self.asset_make.id),
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_asset_make(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            f'{self.asset_make_urls}{self.asset_make.id}/',
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))

        self.assertIn('make_label', response.data.keys())
        self.assertIn(self.asset_make.make_label,
                      response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_api_endpoint_cant_allow_put(self,
                                                    mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.put(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_api_endpoint_cant_allow_patch(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.patch(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_make_api_endpoint_cant_allow_delete(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.asset_make_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
