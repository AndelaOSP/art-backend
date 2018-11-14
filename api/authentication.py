from decouple import config
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from firebase_admin import auth, credentials, initialize_app

ADMIN_USER = 'admin'
SUPERUSER = 'superuser'

User = get_user_model()

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
            uid = token.get('uid')
            user = User.objects.get(email=email)
            if uid:
                attrs = {
                    ADMIN_USER: user.is_staff,
                    SUPERUSER: user.is_superuser,
                }
                auth.set_custom_user_claims(uid, attrs)

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        return (user, token)
