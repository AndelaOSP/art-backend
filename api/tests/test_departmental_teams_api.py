# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from rest_framework import status
from rest_framework.test import APIClient

# App Imports
from api.serializers import AssetSerializer
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, AssetStatus

client = APIClient()


class DepartmentTeamTestCase(APIBaseTestCase):
    """
    Test department teams api
    """

    def test_non_authenticated_user_get_department_teams(self):
        response = client.get(self.departmental_teams_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_department_teams(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.departmental_teams_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        data = response.json()
        assert isinstance(data['results'], list)
        assert response.status_code == status.HTTP_200_OK

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_specific_department_teams_no_data(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        url = "{}/{}/".format(self.departmental_teams_url, self.departmental_team_1.id)
        response = client.get(
            url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "assets_assigned" in data

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_specific_department_teams_with_data(
        self, mock_verify_token
    ):
        # add an asset with and assign it to a team
        new_asset = apps.get_model("core", "Asset").objects.create(
            asset_code="IC001489",
            serial_number="SN00123489",
            purchase_date="2018-07-10",
            model_number=self.assetmodel,
            asset_location=self.centre,
            department=self.department,
            team_name=self.departmental_team,
        )
        AssetStatus.objects.create(asset=new_asset, current_status="Available")
        allocation = AllocationHistory.objects.create(
            asset=new_asset, current_assignee=self.asset_assignee_team
        )
        # authenticate a user
        mock_verify_token.return_value = {"email": self.admin_user.email}
        url = "{}/{}/".format(self.departmental_teams_url, self.departmental_team.id)
        team_response = client.get(
            url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        asset = AssetSerializer(new_asset).data
        assert asset['assigned_to']['name'] == self.departmental_team.name

        data = team_response.json()
        assert team_response.status_code == status.HTTP_200_OK
        assert "assets_assigned" in data
        assert len(data['assets_assigned']['results']) == 1

        AllocationHistory.objects.get(id=allocation.id).delete()

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_add_department_teams(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        payload = {
            "name": "Team 1",
            "description": "string",
            "department": self.department.id,
        }
        response = client.post(
            self.departmental_teams_url,
            data=payload,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        data = response.json()
        assert isinstance(data, dict)
        assert response.status_code == status.HTTP_201_CREATED
