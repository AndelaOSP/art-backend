from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ..models import CheckinCheckout, ItemModelNumber, Item, SecurityUser

User = get_user_model()
client = APIClient()


class CheckinModelTest(TestCase):
    """Tests for the Checkin Model"""

    def setUp(self):
        self.test_itemmodel = ItemModelNumber(model_number="IMN50987")
        self.test_itemmodel.save()

        self.normal_user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )

        self.test_item = Item(
            item_code="IC001",
            serial_number="SN001",
            model_number=self.test_itemmodel,
            assigned_to=self.normal_user
        )
        self.test_item.save()

        self.test_other_item = Item(
            item_code="IC001",
            serial_number="SN001",
            model_number=self.test_itemmodel,
            assigned_to=self.normal_user
        )
        self.test_other_item.save()

        self.security_user = SecurityUser.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )
        self.checkin = CheckinCheckout.objects.create(
            security_user=self.security_user,
            item=self.test_item,
            option="Checkin"
        )
        self.checkout = CheckinCheckout.objects.create(
            security_user=self.security_user,
            item=self.test_item,
            option="Checkout"
        )

        self.token_security_user = 'test_token'
        self.token_normal_user = 'test_other_token'

        self.checkin_checkout_url = reverse('checkin-checkout-list')

    def test_add_checkin(self):
        CheckinCheckout.objects.create(
            security_user=self.security_user,
            item=self.test_other_item,
            option="Checkin"
        )
        self.assertEqual(CheckinCheckout.objects.count(), 3)

    def test_add_checkout(self):
        CheckinCheckout.objects.create(
            security_user=self.security_user,
            item=self.test_other_item,
            option="Checkout"
        )
        self.assertEqual(CheckinCheckout.objects.count(), 3)

    def test_delete_checkin(self):
        self.assertEqual(CheckinCheckout.objects.count(), 2)
        self.checkin.delete()
        self.assertEqual(CheckinCheckout.objects.count(), 1)

    def test_update_checkin(self):
        self.checkin.item = self.test_other_item
        self.checkin.save()
        self.assertEqual(self.checkin.item.item_code,
                         self.test_other_item.item_code)

    def test_update_checkout(self):
        self.checkout.item = self.test_other_item
        self.checkout.save()
        self.assertEqual(self.checkout.item.item_code,
                         self.test_other_item.item_code)

    def test_non_authenticated_user_checkin_checkout(self):
        response = client.get(self.checkin_checkout_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_checkout_model_string_representation(self):
        self.assertEqual(str(self.checkin), self.test_item.serial_number)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_normal_user_list_checkin_checkout(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        response = client.get(
            self.checkin_checkout_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_normal_user))
        self.assertEqual(response.data, {
            'detail': 'You do not have permission to perform this action.'
        })
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_list_checkin_checkout(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.get(
            self.checkin_checkout_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertIn(self.checkin.id, response.data[0].values())
        self.assertEqual(len(response.data), CheckinCheckout.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_normal_user_create_checkin(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        response = client.get(
            self.checkin_checkout_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_normal_user))
        self.assertEqual(response.data, {
            'detail': 'You do not have permission to perform this action.'
        })
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkin(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {
            'item': self.test_other_item.id,
            'security_user': self.security_user.id,
            'option': 'Checkin'
        }
        response = client.post(
            self.checkin_checkout_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data['item'], self.test_other_item.id)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkout(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {
            'item': self.test_other_item.id,
            'security_user': self.security_user.id,
            'option': 'Checkout'
        }
        response = client.post(
            self.checkin_checkout_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data['item'], self.test_other_item.id)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_with_invalid_option(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        option = "Invalid"
        data = {
            'item': self.test_other_item.id,
            'security_user': self.security_user.id,
            'option': option
        }
        response = client.post(
            self.checkin_checkout_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data, {
            'option': ['"{}" is not a valid choice.'.format(option)]
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_create_checkin_without_item(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        data = {
            'security_user': self.security_user.id
        }
        response = client.post(
            self.checkin_checkout_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data, {
            'item': ['This field is required.']
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_view_checkin_detail(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.get(
            "{}{}/".format(self.checkin_checkout_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data['id'], self.checkin.id)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_delete_checkin(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.delete(
            "{}{}/".format(self.checkin_checkout_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_put_checkin(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.put(
            "{}{}/".format(self.checkin_checkout_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_security_user_cannot_patch_checkin(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.security_user.email}
        response = client.patch(
            "{}{}/".format(self.checkin_checkout_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_security_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
