from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
client = APIClient()


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', cohort=20,
            slack_handle='@test_user', password='devpassword'
        )
        self.token_user = 'testtoken'
        self.admin_user = User.objects.create_superuser(
            email='admin@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_admin = 'admintesttoken'
        self.users_url = "/api/v1/users/"

    def test_can_add_user(self):
        users_count_before = User.objects.count()
        new_user = User.objects.create(
            email='test-1@site.com', cohort=20,
            slack_handle='@test_user-1', password='devpassword'
        )
        users_count_after = User.objects.count()
        self.assertEqual(new_user.email, 'test-1@site.com')
        self.assertEqual(new_user.cohort, 20)
        self.assertEqual(new_user.slack_handle, '@test_user-1')
        self.assertEqual(new_user.password, 'devpassword')
        self.assertEqual(users_count_before, users_count_after - 1)

    def test_add_user_without_password(self):
        users_count_before = User.objects.count()
        new_user = User.objects.create(
            email='test-1@site.com', cohort=20,
            slack_handle='@test_user-1'
        )
        users_count_after = User.objects.count()
        self.assertEqual(new_user.password, None)
        self.assertEqual(users_count_before, users_count_after - 1)

    def test_can_update_user(self):
        self.user.name = 'edited_name'
        self.user.save()
        self.assertIn("edited_name", self.user.name)

    def test_can_delete_a_user(self):
        new_user = User.objects.create(
            email='test-1@site.com', cohort=20,
            slack_handle='@test_user-1', password='devpassword'
        )
        users_count_before = User.objects.count()
        new_user.delete()
        users_count_after = User.objects.count()
        self.assertEqual(users_count_before, users_count_after + 1)

    def test_user_model_string_representation(self):
        self.assertEquals(str(self.user), 'test@site.com')

    def test_user_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='', name='test_user1',
                cohort=20, slack_handle='@test_user1',
                password='devpassword')

    def test_user_cohort_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test1@site.com', name='test_name',
                cohort='', slack_handle='@test_user1',
                password='devpassword')

    def test_user_slack_handle_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test1@site.com', name='test_name',
                cohort=20, slack_handle='',
                password='devpassword')

    def test_create_normal_user(self):
        new_user_1 = User.objects.create_user(
            email='test-1@site.com', cohort=20,
            slack_handle='@test_user-1', password='devpassword'
        )
        new_user_2 = User.objects._create_user(
            email='test-2@site.com', cohort=20,
            slack_handle='@test_user-2', password='devpassword'
        )
        self.assertFalse(new_user_1.is_staff)
        self.assertFalse(new_user_1.is_superuser)
        self.assertFalse(new_user_2.is_staff)
        self.assertFalse(new_user_2.is_superuser)

    def test_create_superuser(self):
        new_user_1 = User.objects.create_superuser(
            email='test-2@site.com', cohort=20,
            slack_handle='@test_user-2', password='devpassword'
        )
        self.assertTrue(new_user_1.is_staff)
        self.assertTrue(new_user_1.is_superuser)

    def test_create_superuser_with_staff_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='test-2@site.com', cohort=20,
                slack_handle='@test_user-2', password='devpassword',
                is_staff=False, is_superuser=True
            )

    def test_create_superuser_with_superuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='test-2@site.com', cohort=20,
                slack_handle='@test_user-2', password='devpassword',
                is_staff=True, is_superuser=False
            )

    def test_non_authenticated_user_add_user_from_api_endpoint(self):
        response = client.post(self.users_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 401)

    def test_non_authenticated_user_get_user_from_api_endpoint(self):
        response = client.get(self.users_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 401)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_add_user_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.post(
            self.users_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'You do not have permission to perform this action.'
        })
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_user_et_user_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.users_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'You do not have permission to perform this action.'
        })
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_user_add_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        users_count_before = User.objects.count()
        data = {
            "password": "devpassword",
            "email": "test_user@mail.com",
        }
        response = client.post(
            self.users_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        users_count_after = User.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(users_count_after, users_count_before + 1)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_user_get_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.users_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(len(response.data), User.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_not_found_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': 'unavailable@email.com'}
        response = client.get(
            self.users_url,
            HTTP_AUTHORIZATION="Token {}".format('sometoken'))
        self.assertEqual(response.data, {
            'detail': 'Unable to authenticate.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_inactive_user_from_api_endpoint(self, mock_verify_token):
        self.admin_user.is_active = False
        self.admin_user.save()
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.users_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'User inactive or deleted.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_add_user_from_api_endpoint_without_email(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {
            "password": "devpassword",
            "email": "",
        }
        response = client.post(
            self.users_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'email': ['This field may not be blank.']
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_add_user_api_endpoint_cant_allow_put(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        user = User.objects.filter(
            email='test@site.com').first()
        response = client.put(
            '{}{}/'.format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_add_user_api_endpoint_cant_allow_patch(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        user = User.objects.filter(
            email='test@site.com').first()
        response = client.patch(
            '{}{}/'.format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_add_user_api_endpoint_cant_allow_delete(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        user = User.objects.filter(
            email='test@site.com').first()
        response = client.delete(
            '{}{}/'.format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
