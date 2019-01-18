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


class AndelaCentreAPITest(APIBaseTestCase):
    """ Tests for the Andela Centre endpoint"""

    def test_non_authenticated_user_get_centres(self):
        response = client.get(self.centre_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_centre(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"centre_name": "ET", "country": self.country.id}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("centre_name", response.data.keys())
        self.assertEqual(response.data.get('country'), self.country.name)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_centre_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        center = AndelaCentre.objects.first()
        data = {"centre_name": center.centre_name, "country": center.country}
        response = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("centre_name", response.data.keys())
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_editing_centre(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {"centre_name": "Matoke", "country": self.country.id}
        res = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        centre_url = reverse('andela-centres-detail', args={res.data.get("id")})
        country, _ = Country.objects.get_or_create(name='Rwanda')
        res = client.put(
            centre_url,
            data={"centre_name": "Gorilla", "country": country.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(res.data["centre_name"], "Gorilla")
        self.assertEqual(res.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_delete_centre(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {"centre_name": "Test", "country": self.country.id}

        res = client.post(
            self.centre_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        centre_url = reverse('andela-centres-detail', args={res.data.get("id")})

        response = client.delete(
            centre_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data, {'detail': 'Deleted Successfully'})
        self.assertEqual(response.status_code, 204)

    @patch('api.authentication.auth.verify_id_token')
    def test_country_create(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"name": countries.lookup('Rwanda').name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_duplicate_country_create(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"name": self.country.name}
        response = client.post(
            self.country_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.admin_user),
        )
        self.assertEqual(response.status_code, 400)
