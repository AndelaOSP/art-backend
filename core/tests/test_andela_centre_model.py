from django.db import IntegrityError
from django.db import transaction
from ..models import AndelaCentre

from core.tests import CoreBaseTestCase


class AndelaCentreModelTest(CoreBaseTestCase):
    """ Tests for the Andela Centre Model """

    def setUp(self):
        super(AndelaCentreModelTest, self).setUp()
        self.centre = AndelaCentre.objects.create(centre_name="ET", country="Nigeria")
        self.centre = AndelaCentre.objects.get(centre_name="ET")

    def test_can_save_a_centre(self):
        AndelaCentre.objects.create(centre_name="Gorilla", country="Rwanda")
        new_centre = AndelaCentre.objects.get(centre_name="Gorilla")
        new_centre_count = AndelaCentre.objects.count()

        self.assertEqual(new_centre_count, 2)
        self.assertIn(new_centre.centre_name, "Gorilla")

    def test_cannot_add_existing_centre_name(self):
        self.assertEqual(AndelaCentre.objects.count(), 1)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                new_centre = AndelaCentre.objects.create(centre_name="ET")
                new_centre.save()

        self.assertEqual(AndelaCentre.objects.count(), 1)

    def test_can_edit_a_centre(self):
        self.centre.centre_name = "The dojo"
        self.centre.save()
        self.assertIn("The dojo", self.centre.centre_name)

    def test_can_delete_a_centre(self):
        new_centre = AndelaCentre.objects.create(centre_name="The dojo", country="Kenya")
        new_centre_count = AndelaCentre.objects.count()
        new_centre.delete()
        count_after_deletion = AndelaCentre.objects.count()

        self.assertEqual(new_centre_count, 2)
        self.assertEqual(count_after_deletion, 1)

    def test_asset_centre_model_string_representation(self):
        self.assertEquals(str(self.centre), "ET")
