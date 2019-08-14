# Standard Library
from unittest.mock import patch

# Third-Party Imports
from pycountry import countries
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError

# App Imports
from api.tests import APIBaseTestCase
from core.models import AndelaCentre, Country

client = APIClient()


class Post_CountryApiTest(APIBaseTestCase):
    """ Tests creation of country endpoint"""

    def test_non_authenticated_users_cannot_add_country(self):
        data = {"name": "Uganda"}
        response = client.post(self.country_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_country_create(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": countries.lookup("Rwanda").name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_add_duplicate_country(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": self.country.name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertEqual(
            response.data["name"][0], "country with this name already exists."
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_add_invalid_country(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "oiuytre"}
        with self.assertRaises(ValidationError):
            response = client.post(
                self.country_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
            )

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_add_country_with_empty_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": None}
        with self.assertRaises(ValidationError):
            response = client.post(
                self.country_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
            )


class Get_CountryApiTest(APIBaseTestCase):
    "Test fetching of countries"

    def test_non_authenticated_users_cannot_get_countries(self):
        response = client.get(self.country_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_get_country_by_id(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        country_url = reverse("countries-detail", args={self.country.id})
        res = client.get(
            country_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(res.data["name"], self.country.name)
        self.assertEqual(res.data["id"], self.country.id)
        self.assertEqual(res.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_get_countries(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        res = client.get(
            self.country_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(res.data["results"][0]["name"], self.country.name)
        self.assertEqual(res.data["results"][0]["id"], self.country.id)
        self.assertEqual(res.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_get_country_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        country_url = reverse("countries-detail", args={209})
        res = client.get(
            country_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(res.data["detail"], "Not found.")
        self.assertEqual(res.status_code, 404)


class Edit_CountryApiTest(APIBaseTestCase):
    "Test editing of countries"

    def test_non_authenticated_users_cannot_update_countries(self):
        data = {"name": "Uganda"}
        country_url = reverse("countries-detail", args={self.country.id})
        response = client.get(country_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_editing_country_succeeds(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Chad"}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        country_url = reverse("countries-detail", args={response.data.get("id")})
        res = client.put(
            country_url,
            data={"name": "Gabon"},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data["name"], "Gabon")
        self.assertEqual(res.data["id"], response.data["id"])
        self.assertEqual(res.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_edit_country_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Uganda"}
        country_url = reverse("countries-detail", args={200})
        res = client.put(
            country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data["detail"], "Not found.")
        self.assertEqual(res.status_code, 404)


class Delete_CountryApiTest(APIBaseTestCase):
    "Test deleting of countries"

    def test_non_authenticated_users_cannot_delete_country(self):
        centre_url = reverse("andela-centres-detail", args={self.centre.id})
        response = client.delete(centre_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_delete_country(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Burundi"}

        res = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        country_url = reverse("countries-detail", args={res.data.get("id")})

        response = client.delete(
            country_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_delete_country_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        country_url = reverse("countries-detail", args={200})
        res = client.delete(
            country_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(res.data["detail"], "Not found.")
        self.assertEqual(res.status_code, 404)
