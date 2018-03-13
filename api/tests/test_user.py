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
        self.admin_user = User.objects.create_superuser(
            email='admin@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )

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
        response = client.post('/api/v1/user/')
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 403)

    def test_non_authenticated_user_get_user_from_api_endpoint(self):
        response = client.get('/api/v1/user/')
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 403)

    def test_non_admin_user_add_user_from_api_endpoint(self):
        client.login(username='test@site.com', password='devpassword')
        response = client.post('/api/v1/user/')
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 403)

    def test_non_admin_user_et_user_from_api_endpoint(self):
        client.login(username='test@site.com', password='devpassword')
        response = client.get('/api/v1/user/')
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })
        self.assertEqual(response.status_code, 403)

    def test_admin_user_add_users_from_api_endpoint(self):
        users_count_before = User.objects.count()
        client.login(username='admin@site.com', password='devpassword')
        data = {
            "password": "devpassword",
            "email": "test_user@mail.com",
        }
        response = client.post('/api/v1/user/', data=data, format='json')
        users_count_after = User.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(users_count_after, users_count_before + 1)

    def test_admin_user_get_users_from_api_endpoint(self):
        client.login(username='admin@site.com', password='devpassword')
        response = client.get('/api/v1/user/')
        self.assertEqual(len(response.data), User.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_add_user_from_api_endpoint_without_password(self):
        client.login(username='admin@site.com', password='devpassword')
        data = {
            "password": "",
            "email": "test_user@mail.com",
        }
        response = client.post('/api/v1/user/', data=data, format='json')
        self.assertEqual(response.data, {
            'password': ['This field may not be blank.']
        })
        self.assertEqual(response.status_code, 400)

    def test_add_user_from_api_endpoint_without_email(self):
        client.login(username='admin@site.com', password='devpassword')
        data = {
            "password": "devpassword",
            "email": "",
        }
        response = client.post('/api/v1/user/', data=data, format='json')
        self.assertEqual(response.data, {
            'email': ['This field may not be blank.']
        })
        self.assertEqual(response.status_code, 400)
