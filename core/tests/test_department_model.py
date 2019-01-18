# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

# App Imports
from core.models import Department
from core.tests import CoreBaseTestCase

User = get_user_model()


class DepartmentModelTest(CoreBaseTestCase):
    """Tests for the Department Model"""

    def test_add_department(self):
        """Test add new department"""
        count = Department.objects.count()
        new_department = Department(name="People")
        new_department.save()
        self.assertEqual(Department.objects.count(), count + 1)

    def test_cannot_add_existing_department(self):
        """Test cannot add existing department"""
        count = Department.objects.count()
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                Department.objects.create(name=self.department.name)

        self.assertEqual(Department.objects.count(), count)

    def test_department_model_string_representation(self):
        self.assertEqual(str(self.department), self.department.name)
