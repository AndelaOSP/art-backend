# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# App Imports
from core.models import AssetAssignee, Department, OfficeWorkspace
from core.tests import CoreBaseTestCase

User = get_user_model()


class AssetAssigneeModelTest(CoreBaseTestCase):
    """Tests for AssetAssignee Model"""

    def test_invalid_user_email(self):
        with self.assertRaises(ValidationError):
            User.objects.create(
                email='test100@gmail.com', cohort=10, password='devpassword'
            )

    def test_asset_assignee_is_created_when_a_user_is_saved(self):
        """
        Test every time a user is created, an asset assignee
         associated with this user is created
        """
        user = User.objects.create(
            email='test100@andela.com', cohort=10, password='devpassword'
        )
        self.assertEqual(len(AssetAssignee.objects.filter(user=user)), 1)

    def test_asset_assignee_is_created_when_a_department_is_saved(self):
        """
        Test every time a new department is saved,
        an associated asset assignee is created.
        """
        department = Department.objects.create(name="Success")
        self.assertEqual(len(AssetAssignee.objects.filter(department=department)), 1)

    def test_asset_assignee_is_created_when_a_workspace_is_saved(self):
        """
        Test every time a new department is saved,
        an associated asset assignee is created.
        """
        workspace = OfficeWorkspace.objects.create(
            name="Success", section=self.office_section
        )
        self.assertEqual(len(AssetAssignee.objects.filter(workspace=workspace)), 1)
