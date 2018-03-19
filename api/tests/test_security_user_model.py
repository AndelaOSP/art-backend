from django.test import TestCase
from ..models import SecurityUser


class SecurityUserModelTest(TestCase):
    """ Tests for the Security User Model """

    def setUp(self):
        SecurityUser.objects.create(
            first_name="TestFirst",
            last_name="TestLast",
            phone="254720900900",
            security_badge_number="AE23"
        )

        self.security_user = SecurityUser.objects.get(
            security_badge_number="AE23"
        )

    def test_can_save_a_security_user(self):
        SecurityUser.objects.create(
            first_name="NewPerson",
            last_name="LastName",
            phone="254720400400",
            security_badge_number="AE34"
        )
        new_security_user = SecurityUser.objects.get(
            security_badge_number="AE34"
        )

        self.assertEqual(SecurityUser.objects.count(), 2)
        self.assertIn("NewPerson", new_security_user.first_name)

    def test_can_edit_a_security_user(self):
        self.security_user.first_name = "Reed"
        self.security_user.last_name = "Richards"
        self.security_user.security_badge_number = "AE31"

        self.security_user.save()
        self.assertIn("AE31", self.security_user.security_badge_number)
