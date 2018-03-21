from django.test import TestCase
from ..models import SecurityUser


class SecurityUserModelTest(TestCase):
    """ Tests for the Security User Model """
    def setUp(self):
        SecurityUser.objects.create(
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )

        self.security_user = SecurityUser.objects.get(
            badge_number="AE23"
        )

    def test_can_save_a_security_user(self):
        SecurityUser.objects.create(
            password="devpassword2",
            first_name="NewPerson",
            last_name="LastName",
            phone_number="254720400400",
            badge_number="AE34"
        )
        new_security_user = SecurityUser.objects.get(
            badge_number="AE34"
        )

        self.assertEqual(SecurityUser.objects.count(), 2)
        self.assertIn("NewPerson", new_security_user.first_name)

    def test_can_edit_a_security_user(self):
        self.security_user.first_name = "Reed"
        self.security_user.last_name = "Richards"
        self.security_user.badge_number = "AE31"

        self.security_user.save()
        self.assertIn("AE31", self.security_user.badge_number)

    def test_can_delete_a_security_user(self):
        new_security_member = SecurityUser.objects.create(
            password="devpassword2",
            first_name="NewPerson",
            last_name="LastName",
            phone_number="254720400400",
            badge_number="AE34"
        )
        new_security_team = SecurityUser.objects.count()

        new_security_member.delete()
        self.assertEqual(new_security_team, 2)
        self.assertEqual(SecurityUser.objects.count(), 1)
