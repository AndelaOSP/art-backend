# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, AndelaCentre, AssetStatus

User = get_user_model()
client = APIClient()


class UserTestCase(APIBaseTestCase):
    def test_can_add_user(self):
        users_count_before = User.objects.count()
        new_user = User.objects.create(
            email="test-1@andela.com", cohort=20, password="devpassword"
        )
        users_count_after = User.objects.count()
        self.assertEqual(new_user.email, "test-1@andela.com")
        self.assertEqual(new_user.cohort, 20)
        self.assertEqual(new_user.password, "devpassword")
        self.assertEqual(users_count_before, users_count_after - 1)

    def test_add_user_without_password(self):
        users_count_before = User.objects.count()
        new_user = User.objects.create(email="test-1@andela.com", cohort=20)
        users_count_after = User.objects.count()
        self.assertEqual(new_user.password, None)
        self.assertEqual(users_count_before, users_count_after - 1)

    def test_can_update_user(self):
        self.user.name = "edited_name"
        self.user.save()
        self.assertIn("edited_name", self.user.name)

    def test_can_delete_a_user(self):
        new_user = User.objects.create(
            email="test-1@andela.com", cohort=20, password="devpassword"
        )
        users_count_before = User.objects.count()
        new_user.delete()
        users_count_after = User.objects.count()
        self.assertEqual(users_count_before, users_count_after + 1)

    def test_user_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", name="test_user1", cohort=20, password="devpassword"
            )

    def test_create_normal_user(self):
        new_user_1 = User.objects.create_user(
            email="test-1@andela.com", cohort=20, password="devpassword"
        )
        new_user_2 = User.objects._create_user(
            email="test-2@andela.com", cohort=20, password="devpassword"
        )
        self.assertFalse(new_user_1.is_staff)
        self.assertFalse(new_user_1.is_superuser)
        self.assertFalse(new_user_2.is_staff)
        self.assertFalse(new_user_2.is_superuser)

    def test_create_superuser(self):
        new_user_1 = User.objects.create_superuser(
            email="test-2@andela.com", cohort=20, password="devpassword"
        )
        self.assertTrue(new_user_1.is_staff)
        self.assertTrue(new_user_1.is_superuser)

    def test_create_superuser_with_staff_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test-2@andela.com",
                cohort=20,
                password="devpassword",
                is_staff=False,
                is_superuser=True,
            )

    def test_create_superuser_with_superuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test-2@andela.com",
                cohort=20,
                password="devpassword",
                is_staff=True,
                is_superuser=False,
            )

    def test_cannot_add_user_without_andela_email(self):
        with self.assertRaises(ValidationError):
            User.objects.create(
                email="wrongemail@gmail.com", cohort=20, password="devpassword"
            )

    def test_cannot_add_superuser_without_andela_email(self):
        with self.assertRaises(ValidationError):
            User.objects.create_superuser(
                email="bademail@gmail.com", cohort=20, password="devpassword"
            )

    def test_non_authenticated_user_add_user_from_api_endpoint(self):
        response = client.post(self.users_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_non_existent_user_add_user_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {"email": "test@notfound.com"}
        response = client.post(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format("sometoken")
        )
        self.assertEqual(response.status_code, 401)

    def test_non_authenticated_user_get_user_from_api_endpoint(self):
        response = client.get(self.users_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_add_user_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.post(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {"detail": "You do not have permission to perform this action."},
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_user_et_user_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {"detail": "You do not have permission to perform this action."},
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_add_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        users_count_before = User.objects.count()
        data = {
            "password": "devpassword",
            "email": "test_user@andela.com",
            "department": "Finance",
        }
        response = client.post(
            self.users_url,
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        users_count_after = User.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(users_count_after, users_count_before + 1)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_get_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(len(response.data["results"]), User.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_can_get_users_from_their_centres_from_api_endpoint(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        location = AndelaCentre.objects.create(name="Kampala", country=self.country)
        User.objects.create(
            email="test1@andela.com",
            cohort=20,
            password="devpassword",
            location=location,
        )
        self.assertEqual(len(response.data["results"]), User.objects.count() - 1)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_inactive_user_from_api_endpoint(self, mock_verify_token):
        self.admin_user.is_active = False
        self.admin_user.save()
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.users_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.data, {"detail": "User inactive or deleted."})

    @patch("api.authentication.auth.verify_id_token")
    def test_add_user_from_api_endpoint_without_email(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"password": "devpassword", "email": ""}
        response = client.post(
            self.users_url,
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"email": ["This field may not be blank."]})
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_add_user_api_endpoint_cant_allow_put(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        user = User.objects.first()
        response = client.put(
            "{}/{}/".format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.json(), {"detail": 'Method "PUT" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_user_api_endpoint_can_allow_patch(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        user = User.objects.first()
        response = client.patch(
            "{}/{}/".format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertTrue(response.status_code == 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_api_endpoint_allow_patch_for_is_staff_attr(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        user = UserTestCase.user
        update_data = {"is_staff": True}
        response = client.patch(
            "{}/{}/".format(self.users_url, user.id),
            data=update_data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        is_staff = User.objects.get(pk=user.id).is_staff
        self.assertFalse(user.is_staff)
        self.assertTrue(is_staff)

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_user_cant_update_is_staff_attr_of_user_from_api(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.user.email}
        user = UserTestCase.user
        update_data = {"is_staff": True}
        response = client.patch(
            "{}/{}/".format(self.users_url, user.id),
            data=update_data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 403)
        updated_is_staff = User.objects.get(pk=user.id).is_staff
        self.assertEqual(user.is_staff, updated_is_staff)
        self.assertFalse(updated_is_staff)

    @patch("api.authentication.auth.verify_id_token")
    def test_user_api_endpoint_cant_allow_delete(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        user = User.objects.first()
        response = client.delete(
            "{}/{}/".format(self.users_url, user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.json(), {"detail": 'Method "DELETE" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_allocated_asset_count(self, mock_verify_token):
        """Test allocated_asset_count returns count of assets allocated to a user"""
        mock_verify_token.return_value = {"email": self.admin_user.email}
        AssetStatus.objects.create(asset=self.asset, current_status="Available")
        response = client.get(
            "{}/{}/".format(self.users_url, self.user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        count = response.data["allocated_asset_count"]
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.user.assetassignee
        )
        response = client.get(
            "{}/{}/".format(self.users_url, self.user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        after_allocation = response.data["allocated_asset_count"]
        self.assertEqual(after_allocation, count + 1)

        AssetStatus.objects.create(asset=self.asset, current_status="Available")
        response = client.get(
            "{}/{}/".format(self.users_url, self.user.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["allocated_asset_count"], after_allocation - 1)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_filter_users_by_cohort(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?cohort={}".format(self.users_url, self.user.cohort),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["results"][0]["cohort"], self.user.cohort)
        users_count = User.objects.filter(cohort=self.user.cohort).count()
        self.assertEqual(response.data["count"], users_count)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_filter_users_by_multiple_cohorts(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        cohorts = {user.cohort for user in User.objects.all() if user.cohort}
        cohorts_str = ",".join(str(cohort) for cohort in cohorts)
        response = client.get(
            "{}?cohort={}".format(self.users_url, cohorts_str),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )

        self.assertIn(response.data["results"][0]["cohort"], cohorts)
        self.assertEqual(
            response.data["count"], User.objects.filter(cohort__isnull=False).count()
        )
        cohorts_str += ",unspecified"
        response = client.get(
            "{}?cohort={}".format(self.users_url, cohorts_str),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["count"], User.objects.count())

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_filter_users_without_cohort(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?cohort=unspecified".format(self.users_url),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(
            response.data["count"], User.objects.filter(cohort__isnull=True).count()
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_filter_users_by_email(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?email={}".format(self.users_url, self.user.email),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["results"][0]["email"], self.user.email)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_filter_users_by_email_first_letter(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?email={}".format(self.users_url, self.user.email[0:1].upper()),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["results"][0]["email"], self.user.email)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_filter_users_by_invalid_email(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?email={}".format(self.users_url, "sola@gmail.com"),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_filter_users_with_given_alphabet(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?email={}".format(self.users_url, self.user.email[0:3]),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(
            response.data["results"][0]["email"][0:3], self.user.email[0:3]
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_filter_users_by_asset_count(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        allocation_user = AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.user.assetassignee
        )
        response = client.get(
            "{}?asset_count={}".format(self.users_url, 1),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["results"][0]["allocated_asset_count"], 1)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(isinstance(allocation_user, AllocationHistory))
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_filter_users_by_multiple_asset_count_values(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        AssetStatus.objects.create(asset=self.asset, current_status="Available")
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.user.assetassignee
        )
        response = client.get(
            "{}?asset_count=0,1".format(self.users_url),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn(response.data["results"][0]["allocated_asset_count"], [0, 1])
        self.assertEqual(response.data["count"], User.objects.count())
        self.assertEqual(response.status_code, 200)
