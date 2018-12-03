from django.db.models import ProtectedError

from core.models import UserFeedback
from core.tests import CoreBaseTestCase


class UserFeedbackModelTest(CoreBaseTestCase):
    """ Tests for the UserFeedback Model """
    def test_can_save_feedback(self):
        UserFeedback.objects.create(
            reported_by=self.user, message="This is feedback", report_type="feedback"
        )
        count = UserFeedback.objects.count()
        with self.assertRaises(ProtectedError):
            self.user.delete()
        self.assertEqual(UserFeedback.objects.count(), count)
