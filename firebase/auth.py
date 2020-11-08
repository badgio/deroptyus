import os

from django.contrib.auth.backends import BaseBackend

import firebase_admin
from firebase_admin import auth

from .models import FirebaseUser

class FirebaseBackend(BaseBackend):

    creds = firebase_admin.credentials.Certificate(os.getenv("FIREBASE_API_KEY") or 'firebase.json')
    app = firebase_admin.initialize_app(creds)

    def authenticate(self, request, **kwargs):

        firebase_token = request.META.get("HTTP_AUTHORIZATION")
        if not firebase_token:
            return None

        firebase_token = firebase_token.split(" ").pop()

        try:
            decoded_token = auth.verify_id_token(firebase_token)
        except:
            return None

        if not firebase_token or not decoded_token:
            return None

        try:
            firebase_id = decoded_token.get("uid")
        except:
            return None

        try:
            firebase_user = FirebaseUser.objects.get(firebase_id=firebase_id)
            user = firebase_user.user
        except:
            return None

        return user

    def create_user_email_password(self, email, password):

        try:
            firebase_user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            firebase_user = auth.create_user(email=email, password=password, app=self.app)
        except:
            return None

        return firebase_user.uid


class FirebaseError(Exception):
    pass

class NoEntryForUser(Exception):
    pass