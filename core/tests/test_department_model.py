from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Department
from core.tests import CoreBaseTestCase

User = get_user_model()


class DepartmentModelTest(CoreBaseTestCase):
    """Tests for the Department Model"""

    def setUp(self):
        super(DepartmentModelTest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.department = Department.objects.create(
            name="Success"
        )
        self.all_departments = Department.objects.all()
        self.token_user = 'testtoken'

    def test_add_department(self):
        """Test add new department"""
        self.assertEqual(self.all_departments.count(), 1)
        new_department = Department(name="People")
        new_department.save()
        self.assertEqual(self.all_departments.count(), 2)

    def test_cannot_add_existing_department(self):
        """Test cannot add existing department"""
        self.assertEqual(self.all_departments.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                new_department = Department.objects.create(name="Success")
                new_department.save()

        self.assertEqual(self.all_departments.count(), 1)

    def test_department_model_string_representation(self):
        self.assertEqual(str(self.department), "Success")
