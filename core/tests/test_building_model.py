from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import OfficeBlock

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
        self.all_office_blocks = OfficeBlock.objects.all()
        self.token_user = 'testtoken'

    def test_add_new_office_block(self):
        """Test add new office block"""
        self.assertEqual(self.all_office_blocks.count(), 1)
        new_office_block = OfficeBlock(name="Block B")
        new_office_block.save()
        self.assertEqual(self.all_office_blocks.count(), 2)

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

    def test_office_block_model_string_representation(self):
        self.assertEqual(str(self.office_block), "Block A")
