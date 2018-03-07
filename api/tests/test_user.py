from django.test import TestCase

from django.contrib.auth import get_user_model

from ..forms import UserCreationForm, UserChangeForm

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', name='test_user',
            cohort=20, slack_handle='@test_user')

    def test_can_add_user(self):
        users_count_before = User.objects.all().count()
        user = User.objects.create_user(
            email='test1@site.com', name='test_user1',
            cohort=20, slack_handle='@test_user1',
            password='devpassword')
        users_count_after = User.objects.all().count()

        self.assertFalse(user.admin)
        self.assertFalse(user.staff)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_perm)
        self.assertTrue(user.has_module_perms)
        self.assertEqual(users_count_before, users_count_after - 1)

    def test_can_update_user(self):
        self.user.name = 'edited_name'
        self.user.save()
        self.assertIn("edited_name", self.user.name)

    def test_can_delete_a_user(self):
        new_user = User.objects.create(
            email='test1@site.com', name='test_user1',
            cohort=20, slack_handle='@test_user1')
        users_count_before = User.objects.all().count()
        new_user.delete()
        users_count_after = User.objects.all().count()
        self.assertEqual(users_count_before, users_count_after + 1)

    def test_user_model_string_representation(self):
        self.assertEquals(str(self.user), 'test@site.com')

    def test_admin_user_creation_form(self):
        data = {
            'email': 'test@mail.com',
            'name': 'test_user',
            'cohort': 20,
            'slack_handle': '@slack_handle',
            'picture': 'picture_url',
            'password1': 'devpassword',
            'password2': 'devpassword'
        }
        form = UserCreationForm(data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.cohort, data['cohort'])
        self.assertEqual(user.slack_handle, data['slack_handle'])

    def test_admin_user_edit_form(self):
        data = {
            'email': 'test@mail.com',
            'name': 'test_user',
            'cohort': 20,
            'slack_handle': '@slack_handle',
            'picture': 'picture_url',
        }
        form = UserChangeForm(data, initial={'password': ''})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.cohort, data['cohort'])
        self.assertEqual(user.slack_handle,
                         data['slack_handle'])
        self.assertEqual(user.picture, data['picture'])

    def test_create_super_user(self):
        super_admin = User.objects.create_superuser(
            email='test1@site.com', name='test_user1',
            cohort=20, slack_handle='@test_user1',
            password='devpassword')
        self.assertTrue(super_admin.admin)
        self.assertTrue(super_admin.staff)

    def test_create_staff_user(self):
        staff = User.objects.create_staffuser(
            email='test1@site.com', name='test_user1',
            cohort=20, slack_handle='@test_user1',
            password='devpassword')

        self.assertFalse(staff.admin)
        self.assertTrue(staff.staff)

    def test_user_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='', name='test_user1',
                cohort=20, slack_handle='@test_user1',
                password='devpassword')

    def test_user_name_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test1@site.com', name='',
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
