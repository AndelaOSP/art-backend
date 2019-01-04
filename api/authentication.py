# Standard Library
import logging

# Third-Party Imports
from decouple import config
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import auth, credentials, initialize_app
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

ADMIN_USER = 'admin'
SUPERUSER = 'superuser'

User = get_user_model()
logger = logging.getLogger(__name__)

private_key = config('PRIVATE_KEY').replace('\\n', '\n')
payload = {
    'type': 'service_account',
    'project_id': config('PROJECT_ID'),
    'private_key': private_key,
    'client_email': config('CLIENT_EMAIL'),
    'token_uri': 'https://accounts.google.com/o/oauth2/token'
}

cred = credentials.Certificate(payload)
initialize_app(cred)


class FirebaseTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = auth.verify_id_token(key)
        except Exception:
            raise exceptions.AuthenticationFailed('Unable to authenticate.')
        else:
            email = token.get('email')
            user = User.objects.get(email=email)

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        return (user, token)


@receiver(post_save, sender=User)
def set_firebase_custom_claims(sender, instance, created, **kwargs):
    try:
        user = auth.get_user_by_email(instance.email)
    except Exception:
        logger.warning('No user record found for the provided email. Creating one')
        user = auth.create_user(email=instance.email)
    else:
        if user.uid:
            attrs = {
                ADMIN_USER: instance.is_staff,
                SUPERUSER: instance.is_superuser,
            }
            auth.set_custom_user_claims(user.uid, attrs)
