# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory

client = APIClient()
User = get_user_model()


class FilterValuesApiTest(APIBaseTestCase):
    def test_non_authenticated_admin_view_filter_values(self):
        response = client.get(self.filter_values_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_view_filter_values(self, mock_verify_id_token):
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee
        )
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        cohorts = []
        asset_count = []
        User.objects.create(email="nolocation@andela.com", cohort=35)
        for user in User.objects.filter(location=self.admin_user.location):
            cohort_data = {"id": user.cohort, "option": user.cohort}
            assets = user.assetassignee.asset_set.count()
            asset_count_data = {"id": assets, "option": assets}
            if cohort_data not in cohorts and cohort_data.get("id") is not None:
                cohorts.append(cohort_data)
            if asset_count_data not in asset_count:
                asset_count.append(asset_count_data)

        response = client.get(
            self.filter_values_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(cohorts, response.data.get("cohorts"))
        self.assertEqual(asset_count, response.data.get("asset_count"))
        self.assertEqual(response.status_code, 200)
