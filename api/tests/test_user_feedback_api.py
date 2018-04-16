from django.db.models import ProtectedError
from django.test import TestCase
from ..models import UserFeedback


 
class UserFeedbackModelTest(TestCase):
    """ Tests for the UserFeedback endpoint"""

def setUp(self):
        UserFeedback.objects.create(reported_by = "X.Y@andela.com", message = "This is feedback", report_type = "bug")
        self.feedback = UserFeedback.objects.get(reported_by ="X.Y@andela.com")


def test_feedback_without_message(self):
        UserFeedback.objects.create(reported_by = "Y.Y@andela.com", message = "", report_type = "bug")
        feedback = UserFeedback.objects.get(reported_by ="Y.Y@andela.com")
    
    # def test_feedback_without_email(self):
    #     UserFeedback.objects.create(reported_by = "", message = "This is feedback from hawi", report_type = "bug")
    #     self.feedback = UserFeedback.objects.get(message = "This is feedback from hawi",)

    # def test_feedback_with_wrong_report_type(self):
    #     UserFeedback.objects.create(reported_by = "X.Y@andela.com", message = "This is feedback", report_type = "Hawi")
    #     self.feedback = UserFeedback.objects.get(reported_by ="X.Y@andela.com")
