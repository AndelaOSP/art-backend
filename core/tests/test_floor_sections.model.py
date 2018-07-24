from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import OfficeBlock, FloorSection

from core.tests import CoreBaseTestCase

User = get_user_model()


class OfficeBlockModelTest(CoreBaseTestCase):
    """Tests for the OfficeBlock Model"""

    def setUp(self):
        super(OfficeBlockModelTest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.office_block = OfficeBlock.objects.create(
            name="Block A"
        )

        self.floor_section = FloorSection.objects.create(
            floor_number="5th Floor, Big Apple",
            office_block=self.office_block
        )

        self.all_office_blocks = OfficeBlock.objects.all()
        self.floor_section_counts = FloorSection.objects.all()
        self.token_user = 'testtoken'

    def test_floor_section_model_string_representation(self):
        self.assertEqual(str(self.floor_section), "5th Floor, Big Apple")

    def test_add_new_floor_section(self):
        """Test add new floor section"""
        self.assertEqual(self.floor_section_counts.count(), 1)

    def test_cannot_add_existing_floor_section(self):
        """Test cannot add existing office_section name"""
        self.assertEqual(self.floor_section_counts.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                new_floor_section = FloorSection.objects.create(
                    floor_number="5th Floor, Big Apple",
                    office_block=self.office_block
                )
                new_floor_section.save()

        self.assertEqual(self.floor_section_counts.count(), 1)
