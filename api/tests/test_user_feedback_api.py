from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


from core.models import User

client = APIClient()


class UserFeedbackAPITest(TestCase):
    """ Tests for the UserFeedback endpoint"""

    def setUp(self):
        self.user = User.objects.create(
            email='test4@site.com', cohort=20,
            slack_handle='@test_user4', password='devpassword'
        )

        self.feedback_url = reverse('user-feedback-list')
        self.token_user = 'testtoken'

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_feedback(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            "message": "This is a bug",
            "report_type": "bug"
        }
        response = client.post(
            self.feedback_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertIn("created_at", response.data)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_feedback_without_message(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            "report_type": "bug"
        }
        response = client.post(
            self.feedback_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {"message": ["This field is required."]})

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_with_wrong_report_type(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            "message": "This is feedback",
            "report_type": "fellow feedback"
        }
        response = client.post(
            self.feedback_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(
            response.data,
            {"report_type": ["\"fellow feedback\" is not a valid choice."]})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_feedback(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}

        data = {
            "message": "This is some feedback",
            "report_type": "feedback"
        }
        client.post(
            self.feedback_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        response = client.get(
            self.feedback_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.data[0]["message"], "This is some feedback")
