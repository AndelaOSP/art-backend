# Standard Library
from unittest.mock import patch

# Third-Party Imports
from pycountry import countries
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AndelaCentre, Country

client = APIClient()


class Post_AndelaCentreAPITest(APIBaseTestCase):
    """ Tests creation of Andela Centre endpoint"""

    def test_non_authenticated_users_cannot_create_centres(self):
        data = {"name": "ET", "country": self.country.id}
        response = client.post(
            self.centre_url,
            data=data,
        )
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_create_centre(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "ET", "country": self.country.id}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get("country"), self.country.name)
        self.assertEqual(response.data.get("name"), 'ET')

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_centre_by_non_superuser(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        data = {"name": "Crest", "country": self.country.id}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_post_centre_with_missing_field_fails(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "ET"}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"country": ["This field is required."]})

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_post_centre_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        center = AndelaCentre.objects.first()
        data = {"name": center.name, "country": center.country}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 400)


class Get_AndelaCentreAPITest(APIBaseTestCase):
    "Test fetching of andela centres"

    def test_non_authenticated_users_cannot_get_centres(self):
        response = client.get(self.centre_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
    @patch("api.authentication.auth.verify_id_token")
    def test_get_centre_by_id(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        centre_url = reverse("andela-centres-detail", args={self.centre.id})
        res = client.get(
            centre_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data["name"], self.centre.name)
        self.assertEqual(res.data["country"], self.centre.country.name)
        self.assertEqual(res.data["id"], self.centre.id)
        self.assertEqual(res.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_get_centres(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        res = client.get(
            self.centre_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data['results'][0]["name"], self.centre.name)
        self.assertEqual(res.data['results'][0]["country"], self.centre.country.name)
        self.assertEqual(res.data['results'][0]["id"], self.centre.id)
        self.assertEqual(res.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_get_centre_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        centre_url = reverse("andela-centres-detail", args={209})
        res = client.get(
            centre_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data['detail'], 'Not found.')
        self.assertEqual(res.status_code, 404)


class Edit_AndelaCentreAPITest(APIBaseTestCase):
    "Test editing of andela centres"

    def test_non_authenticated_users_cannot_update_centres(self):
        data = {"name": "Matoke", "country": self.country.id}
        centre_url = reverse("andela-centres-detail", args={self.centre.id})
        response = client.get(centre_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_editing_centre_succeeds(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Matoke", "country": self.country.id}
        res = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        centre_url = reverse("andela-centres-detail", args={res.data.get("id")})
        country, _ = Country.objects.get_or_create(name="Rwanda")
        res = client.put(
            centre_url,
            data={"name": "Gorilla", "country": country.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data["name"], "Gorilla")
        self.assertEqual(res.data["country"], country.name)
        self.assertEqual(res.status_code, 200)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_edit_centre_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Matoke", "country": self.country.id}
        centre_url = reverse("andela-centres-detail", args={200})
        res = client.put(
            centre_url, data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data['detail'],'Not found.')
        self.assertEqual(res.status_code, 404)


class Delete_AndelaCentreAPITest(APIBaseTestCase):
    "Test deleting of andela centres"

    def test_non_authenticated_users_cannot_delete_centres(self):
        centre_url = reverse("andela-centres-detail", args={self.centre.id})
        response = client.delete(centre_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
    
    @patch("api.authentication.auth.verify_id_token")
    def test_can_delete_centre(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test", "country": self.country.id}

        res = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        centre_url = reverse("andela-centres-detail", args={res.data.get("id")})

        response = client.delete(
            centre_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data, {"detail": "Deleted Successfully"})
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_delete_centre_with_invalid_id_fails(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        centre_url = reverse("andela-centres-detail", args={200})
        res = client.delete(
            centre_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data['detail'],'Not found.')
        self.assertEqual(res.status_code, 404)    

    @patch("api.authentication.auth.verify_id_token")
    def test_country_create(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": countries.lookup("Rwanda").name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_duplicate_country_create(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": self.country.name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertEqual(response.status_code, 400)
