# Third-Party Imports
import pytest
from django.db import transaction, utils

# App Imports
from core.models import Department, DepartmentalTeam
from core.tests import CoreBaseTestCase


class MyTestCase(CoreBaseTestCase):
    def setUp(self):
        self.new_department = Department(name="Operations")
        self.new_department.save()

    def tearDown(self):
        self.new_department.delete()

    def test_add_department_team(self):
        count = DepartmentalTeam.objects.count()
        new_team = DepartmentalTeam(
            name="Accounts", department_id=self.new_department.id
        )
        new_team.save()
        assert DepartmentalTeam.objects.count() == count + 1
        new_team.delete()

    def test_cannot_add_existing_team(self):
        team = DepartmentalTeam(name="Accounts", department_id=self.new_department.id)
        team.save()
        with transaction.atomic():
            with pytest.raises(utils.IntegrityError):
                DepartmentalTeam.objects.create(
                    name=team.name, department_id=self.new_department.id
                )
        team.delete()

    def test_cannot_add_team_without_associated_department(self):
        with transaction.atomic():
            with pytest.raises(utils.IntegrityError):
                DepartmentalTeam.objects.create(name="new team")
