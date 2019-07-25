# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models.user import User

client = APIClient()


class HistoryAPITest(APIBaseTestCase):
    """ Tests for the Department endpoint"""

    def setUp(self):
        self.history1 = apps.get_model("core", "History").objects.create(
            table_name="core_country",
            user=self.user,
            item_id="12",
            action="POST",
            body="Uganda",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_history_captures_post_update_delete(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Epic Tower", "country": self.country.id}

        # post
        response_post = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response_post.status_code, 201)
        self.assertEqual(response_post.data.get("country"), self.country.name)
        self.assertEqual(response_post.data.get("name"), "Epic Tower")

        # update
        centre_url = reverse(
            "andela-centres-detail", args={response_post.data.get("id")}
        )
        response_put = client.put(
            centre_url,
            data={"name": "Gorilla", "country": self.country.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response_put.data["name"], "Gorilla")
        self.assertEqual(response_put.status_code, 200)

        # delete
        response_delete = client.delete(
            centre_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response_delete.data, {"detail": "Deleted Successfully"})
        self.assertEqual(response_delete.status_code, 204)

        # get history
        response = client.get(
            self.history_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        user_data = User.objects.get(id=response.data["results"][1]["user"])

        self.assertEqual(response.status_code, 200)
        # history for post
        self.assertEqual(
            response.data["results"][1]["item_id"], str(response_post.data["id"])
        )
        self.assertEqual(response.data["results"][1]["action"], "POST")
        self.assertEqual(response.data["results"][1]["user"], user_data.id)
        # history for put
        self.assertEqual(
            response.data["results"][2]["item_id"], str(response_put.data["id"])
        )
        self.assertEqual(response.data["results"][2]["action"], "PUT")
        self.assertEqual(response.data["results"][2]["user"], user_data.id)
        # history for delete
        self.assertEqual(
            response.data["results"][3]["item_id"], str(response_put.data["id"])
        )
        self.assertEqual(response.data["results"][3]["action"], "DELETE")
        self.assertEqual(response.data["results"][3]["user"], user_data.id)

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
