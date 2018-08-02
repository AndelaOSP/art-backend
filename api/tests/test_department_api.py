from unittest.mock import patch

from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, Department

from api.tests import APIBaseTestCase

client = APIClient()


class DepartmentAPITest(APIBaseTestCase):
    """ Tests for the Department endpoint"""

    def setUp(self):
        super(DepartmentAPITest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.department = Department.objects.create(
            name="Success"
        )
        self.department_url = reverse('departments-list')
        self.token_user = 'testToken'

    def test_non_authenticated_user_get_departments(self):
        response = client.get(self.department_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_department(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "People",
        }
        response = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_department_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Success",
        }
        response = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_editing_department(self,
                                mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        name = "People"
        data = {"name": name}
        res = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        department_url = reverse('departments-detail',
                                 args={res.data.get("id")})

        response = client.put(
            department_url,
            data={"name": "Facilities"},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'name': 'Facilities', 'id': res.data.get('id')
        })
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_delete_department(self,
                                   mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {"name": "Big Success"}

        res = client.post(
            self.department_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        department_url = reverse('departments-detail',
                                 args={res.data.get("id")})

        response = client.delete(
            department_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Deleted Successfully'
        })
        self.assertEqual(response.status_code, 204)
