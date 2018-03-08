from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', cohort=20,
            slack_handle='@test_user', password='devpassword'
        )

    def test_can_add_user(self):
        users_count_before = User.objects.count()
        User.objects.create(
            email='test-1@site.com', cohort=20,
            slack_handle='@test_user-1', password='devpassword'
        )
        users_count_after = User.objects.count()
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
