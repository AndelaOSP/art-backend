from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from ..models import Item, ItemModelNumber

User = get_user_model()
client = APIClient()


class ItemTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_user = Token.objects.create(user=self.user)
        self.other_user = User.objects.create_user(
            email='user1@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_other_user = Token.objects.create(user=self.other_user)
        itemmodel = ItemModelNumber(model_number="IMN50987")
        itemmodel.save()
        item = Item(
            item_code="IC001",
            serial_number="SN001",
            assigned_to=self.user,
            model_number=itemmodel,
            status="Allocated"
        )
        item.save()
        self.item = item
        self.items_url = reverse('items-list')

    def test_non_authenticated_user_view_items(self):
        response = client.get(self.items_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_authenticated_non_owner_view_items(self):
        response = client.get(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user))
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), Item.objects.count() - 1)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_owner_view_items(self):
        response = client.get(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.item.item_code, response.data[0].values())
        self.assertEqual(len(response.data), Item.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_authenticated_owner_view_single_item(self):
        response = client.get(
            "{}{}/".format(self.items_url, self.item.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.item.item_code, response.data.values())
        self.assertEqual(response.status_code, 200)

    def test_items_api_endpoint_cant_allow_post(self):
        response = client.post(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data, {
            'detail': 'Method "POST" not allowed.'
        })

    def test_items_api_endpoint_cant_allow_put(self):
        response = client.put(
            '{}{}/'.format(self.items_url, self.item.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })

    def test_items_api_endpoint_cant_allow_patch(self):
        response = client.patch(
            '{}{}/'.format(self.items_url, self.item.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    def test_items_api_endpoint_cant_allow_delete(self):
        response = client.delete(
            '{}{}/'.format(self.items_url, self.item.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
