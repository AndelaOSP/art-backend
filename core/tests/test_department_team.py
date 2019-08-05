# Third-Party Imports
from django.db import utils

# App Imports
from core.models import Department, DepartmentalTeam
from core.tests import CoreBaseTestCase


class MyTestCase(CoreBaseTestCase):
    def setUp(self):
        self.new_department = Department.objects.create(name="Operations")

    def test_add_department_team(self):
        count = DepartmentalTeam.objects.count()
        new_team = DepartmentalTeam(
            name="Accounts", department_id=self.new_department.id
        )
        new_team.save()
        self.assertEqual(DepartmentalTeam.objects.count(), count + 1)
        new_team.delete()

    def test_cannot_add_existing_team(self):
        team = DepartmentalTeam(name="Accounts", department_id=self.new_department.id)
        team.save()
        with self.assertRaises(utils.IntegrityError):
            new_team = DepartmentalTeam(
                name=team.name, department_id=self.new_department.id
            )
            new_team.save()

    def test_cannot_add_team_without_associated_department(self):
        with self.assertRaises(utils.IntegrityError):
            DepartmentalTeam.objects.create(name="new team")
