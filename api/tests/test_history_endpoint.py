# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class HistoryAPITest(APIBaseTestCase):
    """ Tests for the Department endpoint"""

    @patch("api.authentication.auth.verify_id_token")
    def test_get_history(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.history_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data["results"][0]["id"], self.history1.id)
        self.assertEqual(
            response.data["results"][0]["table_name"], self.history1.table_name
        )
        self.assertEqual(response.data["results"][0]["item_id"], self.history1.item_id)
        self.assertEqual(response.data["results"][0]["action"], self.history1.action)
        self.assertEqual(response.data["results"][0]["user"], self.history1.user.id)
        self.assertEqual(response.data["results"][0]["body"], self.history1.body)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_get_history_by_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        url = reverse("history-detail", args={self.history1.id})
        response = client.get(
            url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data["id"], self.history1.id)
        self.assertEqual(response.data["table_name"], self.history1.table_name)
        self.assertEqual(response.data["item_id"], self.history1.item_id)
        self.assertEqual(response.data["action"], self.history1.action)
        self.assertEqual(response.data["user"], self.history1.user.id)
        self.assertEqual(response.data["body"], self.history1.body)
        self.assertEqual(response.status_code, 200)
