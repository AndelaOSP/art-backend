# # Third-Party Imports
# from decouple import config
# from django_q.tasks import async_task

# # App Imports
# from core.constants import MSG, SUBJECT
# from core.models.user import User


# def send_email(data):
#     """"This method sends emails to  users"""
#     for user in User.objects.filter(is_staff=True):
#         async_task(
#             "django.core.mail.send_mail",
#             SUBJECT,
#             MSG.format(data.name),
#             config("EMAIL_SENDER"),
#             [user.email],
#         )
