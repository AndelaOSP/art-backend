from django.test import TestCase
from ..models import User, UserFeedback


class UserFeedbackModelTest(TestCase):
    """ Tests for the UserFeedback Model """

    def setUp(self):
        self.user = User.objects.create(
            email='test8@site.com', cohort=20,
            slack_handle='@test_user8', password='devpassword'
        )

        self.user2 = User.objects.create(
            email='test9@site.com', cohort=20,
            slack_handle='@test_user9', password='devpassword'
        )

        UserFeedback.objects.create(reported_by=self.user,
                                    message="This is a bug",
                                    report_type="bug")
        self.feedback = UserFeedback.objects.get(reported_by=self.user)

    def test_can_save_feedback(self):
        UserFeedback.objects.create(reported_by=self.user2,
                                    message="This is feedback",
                                    report_type="feedback")
        new_feedback = UserFeedback.objects.get(reported_by=self.user2)
        self.assertEqual(UserFeedback.objects.count(), 2)
        self.assertIn(str(new_feedback.reported_by), "test9@site.com")
