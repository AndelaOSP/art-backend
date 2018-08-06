from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import OfficeBlock, OfficeFloor, OfficeFloorSection, \
    OfficeWorkspace

from core.tests import CoreBaseTestCase

User = get_user_model()


class OfficeBlockModelTest(CoreBaseTestCase):
    """Tests for the Office Block Models"""

    def setUp(self):
        super(OfficeBlockModelTest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.office_block = OfficeBlock.objects.create(
            name="Block A"
        )

        self.office_floor = OfficeFloor.objects.create(
            number=5,
            block=self.office_block
        )

        self.office_floor_section = OfficeFloorSection.objects.create(
            name="Right Wing",
            floor=self.office_floor
        )

        self.office_workspace = OfficeWorkspace.objects.create(
            name="DeveloperA Workspace",
            section=self.office_floor_section
        )

        self.all_office_blocks = OfficeBlock.objects.all()
        self.all_office_floors = OfficeFloor.objects.all()
        self.all_office_floor_sections = OfficeFloorSection.objects.all()
        self.all_office_workspaces = OfficeWorkspace.objects.all()
        self.token_user = 'testtoken'

    def test_add_new_office_block(self):
        """Test add new office block"""
        self.assertEqual(self.all_office_blocks.count(), 1)
        new_office_block = OfficeBlock(name="Block B")
        new_office_block.save()
        self.assertEqual(self.all_office_blocks.count(), 2)

    def test_add_new_office_floor(self):
        """Test add new office floor"""
        self.assertEqual(self.all_office_floors.count(), 1)
        new_office_floor = OfficeFloor(
            number=10,
            block=self.office_block)
        new_office_floor.save()
        self.assertEqual(self.all_office_floors.count(), 2)

    def test_add_new_office_floor_section(self):
        """Test add new Office Floor Section"""
        self.assertEqual(self.all_office_floor_sections.count(), 1)
        new_office_floor_section = OfficeFloorSection(
            name="Left Wing",
            floor=self.office_floor)
        new_office_floor_section.save()
        self.assertEqual(self.all_office_floor_sections.count(), 2)

    def test_add_new_office_workspace(self):
        """Test add new office workspace"""
        self.assertEqual(self.all_office_workspaces.count(), 1)
        OfficeWorkspace(
            name="DeveloperB Workspace",
            section=self.office_floor_section
        ).save()
        self.assertEqual(self.all_office_workspaces.count(), 2)

    def test_cannot_add_existing_office_block(self):
        """Test cannot add existing office_block name"""
        self.assertEqual(self.all_office_blocks.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                new_office_block = OfficeBlock.objects.create(
                    name="Block A"
                )
                new_office_block.save()
        self.assertEqual(self.all_office_blocks.count(), 1)

    def test_cannot_add_existing_office_floor_section(self):
        """Test cannot add existing office floor section name"""
        self.assertEqual(self.all_office_floor_sections.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                new_office_floor_section = OfficeFloorSection(
                    name="Right Wing",
                    floor=self.office_floor
                )
                new_office_floor_section.save()
        self.assertEqual(self.all_office_floor_sections.count(), 1)

    def test_cannot_add_existing_office_workspace(self):
        """Test cannot add existing office workspace"""
        self.assertEqual(self.all_office_workspaces.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                OfficeWorkspace(
                    name="DeveloperA Workspace",
                    section=self.office_floor_section
                ).save()
        self.assertEqual(self.all_office_workspaces.count(), 1)

    def test_office_block_model_string_representation(self):
        self.assertEqual(str(self.office_block), "Block A")

    def test_office_floor_model_string_representation(self):
        self.assertEqual(self.office_floor.number, 5)

    def test_office_floor_section_model_string_representation(self):
        self.assertEqual(str(self.office_floor_section), "Right Wing")

    def test_office_workspace_model_string_representation(self):
        self.assertEqual(str(self.office_workspace), "Developera Workspace")
