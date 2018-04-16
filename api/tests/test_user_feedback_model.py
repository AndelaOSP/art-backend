from django.test import TestCase
from ..models import UserFeedback


class UserFeedbackModelTest(TestCase):
    """ Tests for the UserFeedback Model """

    def setUp(self):
        UserFeedback.objects.create(reported_by="X.Y@andela.com",
                                    message="This is feedback",
                                    report_type="bug")
        self.feedback = UserFeedback.objects.get(reported_by="X.Y@andela.com")

    def test_can_save_feedback(self):
        UserFeedback.objects.create(reported_by="user.Y@andela.com",
                                    message="This is feedback",
                                    report_type="bug")
        new_feedback = UserFeedback.objects.get(
            reported_by="user.Y@andela.com")
        new_feedback_count = UserFeedback.objects.count()
        self.assertEqual(new_feedback_count, 2)
        self.assertIn(new_feedback.reported_by, "user.Y@andela.com")
