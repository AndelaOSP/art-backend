# Standard Library
from datetime import datetime
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.constants import CHECKIN, CHECKOUT
from core.models import Asset, AssetLog, AssetMake, AssetModelNumber

User = get_user_model()
client = APIClient()


class AssetLogModelTest(APIBaseTestCase):
    """Tests for the AssetLog Model and API"""

    def setUp(self):
        self.test_asset_make = AssetMake.objects.create(
            name="Test Asset Make", asset_type=self.test_asset_type
        )
        self.test_assetmodel1 = AssetModelNumber.objects.create(
            name="IMN50987", asset_make=self.test_asset_make
        )
        self.test_other_asset = Asset(
            asset_code="IC00sf",
            serial_number="SN00134",
            model_number=self.test_assetmodel1,
            purchase_date="2018-07-10",
            asset_location=self.centre,
        )
        self.test_other_asset.save()
        self.checkin = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type=CHECKIN
        )
        self.checkout = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type=CHECKOUT
        )

    def test_verify_double_checkin_for_asset(self):
        # First log
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        initial_log_count = AssetLog.objects.count()
        # Second log
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        final_log_count = AssetLog.objects.count()
        self.assertEqual(initial_log_count, final_log_count)

    def test_verify_checkin_for_asset_once_checked_in(self):
        # First log
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        # Second log
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        initial_log_count = AssetLog.objects.count()
        # Checkin First log again
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        final_log_count = AssetLog.objects.count()
        self.assertEqual(initial_log_count + 1, final_log_count)

    def test_add_checkin(self):
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        self.assertEqual(AssetLog.objects.count(), 3)
        created_log = AssetLog.objects.filter(asset=self.test_other_asset).first()
        self.assertEqual(created_log.log_type, CHECKIN)

    def test_verify_double_checkout_for_asset(self):
        # First log
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        initial_log_count = AssetLog.objects.count()
        # Second log
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        final_log_count = AssetLog.objects.count()
        self.assertEqual(initial_log_count, final_log_count)

    def test_verify_checkout_for_asset_once_checked_out(self):
        # First log
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        # Second log
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        initial_log_count = AssetLog.objects.count()
        # Checkout First log again
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        final_log_count = AssetLog.objects.count()
        self.assertEqual(initial_log_count + 1, final_log_count)

    def test_add_checkout(self):
        count_before_log = AssetLog.objects.count()
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        self.assertEqual(AssetLog.objects.count(), count_before_log + 1)

    def test_add_checkin_without_log_type(self):
        with self.assertRaises(ValidationError) as e:
            AssetLog.objects.create(
                checked_by=self.security_user, asset=self.test_other_asset
            )

        self.assertEqual(
            e.exception.message_dict,
            {
                "log_type": ["This field cannot be blank."],
                "__all__": ["Log type is required."],
            },
        )

    def test_delete_checkin(self):
        self.assertEqual(AssetLog.objects.count(), 2)
        self.checkin.delete()
        self.assertEqual(AssetLog.objects.count(), 1)

    def test_update_checkin(self):
        self.checkin.asset = self.test_other_asset
        self.checkin.save()
        self.assertEqual(
            self.checkin.asset.asset_code, self.test_other_asset.asset_code
        )

    def test_update_checkout(self):
        self.checkout.asset = self.test_other_asset
        self.checkout.save()
        self.assertEqual(
            self.checkout.asset.asset_code, self.test_other_asset.asset_code
        )

    def test_non_authenticated_user_checkin_checkout(self):
        response = client.get(self.asset_logs_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    def test_checkout_model_string_representation(self):
        self.assertEqual(
            str(self.checkin.asset.serial_number), self.asset.serial_number
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_normal_user_list_checkin_checkout(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_logs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {"detail": "You do not have permission to perform this action."},
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_list_checkin_checkout(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.get(
            self.asset_logs_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertIn(self.checkout.id, response.data["results"][0].values())
        self.assertEqual(len(response.data["results"]), AssetLog.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_list_checkin_checkout(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.asset_logs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertIn(self.checkout.id, response.data["results"][0].values())
        self.assertEqual(len(response.data["results"]), AssetLog.objects.count())
        self.assertEqual(response.status_code, 200)

    # test asset log filters
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_get_filtered_list_of_asset_logs(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = (
            f"{self.asset_logs_url}/?asset_type={self.test_asset_type.name}"
        )
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["asset"],
            f"{self.test_other_asset.serial_number} - {self.test_other_asset.asset_code}",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_get_asset_logs_filtered_by_serial_number(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = (
            f"{self.asset_logs_url}/?asset_serial={self.test_other_asset.serial_number}"
        )
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["asset"],
            f"{self.test_other_asset.serial_number} - {self.test_other_asset.asset_code}",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_get_asset_logs_filtered_by_invalid_serial_number(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}/?asset_serial=SERIALDONTEXIST"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_get_asset_logs_filtered_by_asset_code(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = (
            f"{self.asset_logs_url}/?asset_code={self.test_other_asset.asset_code}"
        )

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["asset"],
            f"{self.test_other_asset.serial_number} - {self.test_other_asset.asset_code}",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_user_get_asset_logs_filtered_by_invalid_asset_code(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}/?asset_serial=CODEDONTEXIST"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_gets_filtered_list_of_asset_logs_by_checked_by(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        asset = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )

        asset_logs_url = f"{self.asset_logs_url}?checked_by={asset.checked_by}"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["checked_by"], f"{self.security_user}"
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_get_of_asset_logs_invalid_filter(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        self.checkin = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}/?asset_type=filterdontexit"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    @patch(
        "django.utils.timezone.now",
        return_value=datetime(2017, 9, 22, 17, 1, 26, 842_150),
    )
    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_year(self, mock_verify_id_token, mock_datetime):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        asset_log = AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )

        asset_logs_url = f"{self.asset_logs_url}?year={mock_datetime.return_value.year}"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        data = response.data["results"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data[0]["created_at"].split("-")[0], f"{asset_log.created_at.year}"
        )
        logs_count = AssetLog.objects.filter(
            created_at__year=mock_datetime.return_value.year
        ).count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_invalid_year(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}?year=5"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        logs_count = AssetLog.objects.filter(created_at__year="5").count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch(
        "django.utils.timezone.now",
        return_value=datetime(2017, 9, 22, 17, 1, 26, 842_150),
    )
    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_month(self, mock_verify_id_token, mock_datetime):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = (
            f"{self.asset_logs_url}?month={mock_datetime.return_value.month}"
        )
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        data = response.data["results"]
        date = datetime.strptime(data[0]["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(date.month, mock_datetime.return_value.month)
        logs_count = AssetLog.objects.filter(
            created_at__month=mock_datetime.return_value.month
        ).count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_invalid_month(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}?month=34"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        logs_count = AssetLog.objects.filter(created_at__month="34").count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch(
        "django.utils.timezone.now",
        return_value=datetime(2017, 9, 22, 17, 1, 26, 842_150),
    )
    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_day(self, mock_verify_id_token, mock_datetime):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}?day={mock_datetime.return_value.day}"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        data = response.data["results"]
        date = datetime.strptime(data[0]["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(date.day, mock_datetime.return_value.day)
        logs_count = AssetLog.objects.filter(
            created_at__day=mock_datetime.return_value.day
        ).count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_by_invalid_day(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}?day=456"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        logs_count = AssetLog.objects.filter(created_at__day="456").count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch(
        "django.utils.timezone.now",
        return_value=datetime(2017, 9, 22, 17, 1, 26, 842_150),
    )
    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_with_collective_attributes(
        self, mock_verify_id_token, mock_datetime
    ):
        """
        Test filter asset logs with 3 date attributes
        i.e year=2019&month=5&day=15
        """
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        year = mock_datetime.return_value.year
        month = mock_datetime.return_value.month
        day = mock_datetime.return_value.day
        asset_logs_url = f"{self.asset_logs_url}?year={year}&month={month}&day={day}"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        data = response.data["results"]
        date = datetime.strptime(data[0]["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(date, mock_datetime.return_value)
        logs_count = AssetLog.objects.filter(
            created_at=mock_datetime.return_value
        ).count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_filter_asset_logs_with_collective_non_matching_attributes(
        self, mock_verify_id_token
    ):
        """
        Test filter asset logs with 3 date attributes
        i.e year=2019&month=5&day=15
        """
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        asset_logs_url = f"{self.asset_logs_url}?year=2077&month=09&day=22"

        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        logs_count = AssetLog.objects.filter(created_at="2077-09-22").count()
        self.assertEqual(len(response.data["results"]), logs_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_normal_user_create_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_logs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(
            response.data,
            {"detail": "You do not have permission to perform this action."},
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_create_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        data = {"asset": self.test_other_asset.id, "log_type": "Checkin"}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data["asset"],
            f"{self.test_other_asset.serial_number} - "
            f"{self.test_other_asset.asset_code}",
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_cannot_double_checkin_an_asset(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        initial_log_count = AssetLog.objects.count()
        data = {"asset": self.test_other_asset.id, "log_type": CHECKIN}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        updated_log_count = AssetLog.objects.count()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(initial_log_count, updated_log_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_that_authenticated_security_user_can_checkin_asset_previously_checked_in(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        # Check in the asset
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        # Checkout the asset
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        initial_log_count = AssetLog.objects.count()
        data = {"asset": self.test_other_asset.id, "log_type": CHECKIN}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        updated_log_count = AssetLog.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(initial_log_count + 1, updated_log_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_can_checkout_asset_previously_checked_out(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        # Check out the asset
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        # Check in the asset
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.test_other_asset, log_type=CHECKIN
        )
        initial_log_count = AssetLog.objects.count()
        data = {"asset": self.test_other_asset.id, "log_type": CHECKOUT}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        updated_log_count = AssetLog.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(initial_log_count + 1, updated_log_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_create_checkout(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        data = {"asset": self.test_other_asset.id, "log_type": CHECKOUT}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data["asset"],
            f"{self.test_other_asset.serial_number} - "
            f"{self.test_other_asset.asset_code}",
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_cannot_double_checkout_an_asset(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        AssetLog.objects.create(
            checked_by=self.security_user,
            asset=self.test_other_asset,
            log_type=CHECKOUT,
        )
        initial_log_count = AssetLog.objects.count()
        data = {"asset": self.test_other_asset.id, "log_type": CHECKOUT}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        updated_log_count = AssetLog.objects.count()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(initial_log_count, updated_log_count)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_create_with_invalid_log_type(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        log_type = "Invalid"
        data = {"asset": self.test_other_asset.id, "log_type": log_type}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(
            response.data,
            {"log_type": ['"{}" is not a valid choice.'.format(log_type)]},
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_create_checkin_without_asset(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        data = {"log_type": "Checkin"}
        response = client.post(
            self.asset_logs_url,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertDictEqual(response.data, {"asset": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_view_checkin_detail(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.get(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data["id"], self.checkin.id)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_cannot_delete_checkin(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_cannot_put_checkin(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.put(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_security_user_cannot_patch_checkin(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.patch(
            "{}/{}/".format(self.asset_logs_url, self.checkin.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_gets_filtered_list_of_asset_logs_by_asset_category(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}

        asset_logs_url = (
            f"{self.asset_logs_url}?asset_category={self.asset_category.name}"
        )
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        asset_log = response.data["results"][0]["asset"]
        asset_code = asset_log.split("-")[1].strip()
        asset = Asset.objects.get(asset_code=asset_code)
        category_name = (
            asset.model_number.asset_make.asset_type.asset_sub_category.asset_category.name
        )
        self.assertEqual(category_name, self.asset_category.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_gets_filtered_list_of_asset_logs_by_sub_asset_category(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}

        asset_logs_url = (
            f"{self.asset_logs_url}?asset_sub_category={self.asset_sub_category.name}"
        )
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        asset_log = response.data["results"][0]["asset"]
        asset_code = asset_log.split("-")[1].strip()
        asset = Asset.objects.get(asset_code=asset_code)
        sub_category_name = (
            asset.model_number.asset_make.asset_type.asset_sub_category.name
        )
        self.assertEqual(sub_category_name, self.asset_sub_category.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_gets_filtered_list_of_asset_logs_by_asset_make(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}

        asset_logs_url = f"{self.asset_logs_url}?asset_make={self.asset_make.name}"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        asset_log = response.data["results"][0]["asset"]
        asset_code = asset_log.split("-")[1].strip()
        asset = Asset.objects.get(asset_code=asset_code)
        asset_make = asset.model_number.asset_make.name
        self.assertEqual(asset_make, self.asset_make.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_user_asset_logs_by_return_detailed_fields(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        asset_logs_url = f"{self.asset_logs_url}"
        response = client.get(
            asset_logs_url, HTTP_AUTHORIZATION=f"Token {self.token_admin}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["asset_make"], self.asset_make.name
        )
        self.assertEqual(
            response.data["results"][0]["asset_type"], self.asset_type.name
        )
        self.assertEqual(
            response.data["results"][0]["asset_sub_category"],
            self.asset_sub_category.name,
        )
        self.assertEqual(
            response.data["results"][0]["asset_category"], self.asset_category.name
        )
