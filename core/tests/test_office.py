from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import OfficeBlock, OfficeFloorSection, OfficeWorkspace, AndelaCentre

from core.tests import CoreBaseTestCase

User = get_user_model()


class OfficeBlockModelTest(CoreBaseTestCase):
    """Tests for the Office Block Models"""

    def test_add_new_office_block(self):
        """Test add new office block"""
        count = OfficeBlock.objects.count()
        OfficeBlock.objects.create(name="Block B", location=self.centre)
        self.assertEqual(OfficeBlock.objects.count(), count + 1)

        """Test add similar named block in diff centers."""
        other_center = AndelaCentre.objects.create(centre_name="Towers", country="Uganda")
        OfficeBlock.objects.create(name="Block B", location=other_center)
        self.assertEqual(OfficeBlock.objects.count(), count + 2)

    def test_cannot_add_existing_office_block(self):
        """Test cannot add existing office_block name"""
        count = OfficeBlock.objects.count()
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                OfficeBlock.objects.create(
                    name=OfficeBlock.objects.first().name,
                    location=self.centre
                )
        self.assertEqual(OfficeBlock.objects.count(), count)

    def test_cannot_add_existing_office_floor_section(self):
        """Test cannot add existing office floor section name"""
        count = OfficeBlock.objects.count()
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                OfficeFloorSection.objects.create(
                    name=OfficeFloorSection.objects.first().name,
                    floor=self.office_floor
                )
        self.assertEqual(OfficeBlock.objects.count(), count)

    def test_cannot_add_existing_office_workspace(self):
        """Test cannot add existing office workspace"""
        count = OfficeWorkspace.objects.count()
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                OfficeWorkspace.objects.create(
                    name=OfficeWorkspace.objects.first().name,
                    section=self.office_section
                )
        self.assertEqual(OfficeWorkspace.objects.count(), count)

    def test_office_block_model_string_representation(self):
        self.assertEqual(str(self.office_block), self.office_block.name)

    def test_office_floor_model_string_representation(self):
        self.assertEqual(str(self.office_floor), str(self.office_floor.number))

    def test_office_floor_section_model_string_representation(self):
        self.assertEqual(str(self.office_section), self.office_section.name)

    def test_office_workspace_model_string_representation(self):
        self.assertEqual(str(self.office_workspace), self.office_workspace.name)
