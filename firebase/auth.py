import firebase_admin
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from firebase_admin import auth

from .models import FirebaseUser


class FirebaseBackend(BaseBackend):
    creds = firebase_admin.credentials.Certificate(settings.FIREBASE_API_KEY)
    app = firebase_admin.initialize_app(creds)

    def authenticate(self, request, **kwargs):

        firebase_token = request.META.get("HTTP_AUTHORIZATION")
        if not firebase_token:
            return None

        firebase_token = firebase_token.split(" ").pop()

        try:
            decoded_token = auth.verify_id_token(firebase_token, app=self.app)
        except Exception:
            raise InvalidIdToken()

        if not firebase_token or not decoded_token:
            return None

        firebase_id = decoded_token.get("uid")

        try:
            firebase_user = FirebaseUser.objects.get(id=firebase_id)
        except FirebaseUser.DoesNotExist:
            raise FirebaseUserDoesNotExist()

        user = firebase_user.user

        return user

    def create_user_email_password(self, email, password):

        try:
            firebase_user = auth.get_user_by_email(email, app=self.app)
        except auth.UserNotFoundError:
            firebase_user = auth.create_user(email=email, password=password, app=self.app)

        return firebase_user.uid

    def get_user_by_id(self, user_id):
        try:
            firebase_user = auth.get_user(user_id, app=self.app)
        except Exception:
            return None

        return firebase_user

    def get_user_by_email(self, email):
        try:
            firebase_user = auth.get_user_by_email(email, app=self.app)
        except auth.UserNotFoundError:
            return None

        return firebase_user.uid

    def delete_user_by_id(self, user_id):
        try:
            auth.delete_user(user_id)
        except Exception:
            pass

    def change_users_email(self, uid, email):
        try:
            auth.update_user(uid=uid, email=email, app=self.app)
        except Exception:
            raise FirebaseError()

    def change_users_password(self, uid, password):
        try:
            auth.update_user(uid=uid, password=password, app=self.app)
        except Exception:
            raise FirebaseError()

    def delete_user(self, uid):
        auth.delete_user(uid, app=self.app)

    def delete_user_by_email(self, email):
        try:
            firebase_user = auth.get_user_by_email(email)
            auth.delete_user(firebase_user.uid, app=self.app)
        except auth.UserNotFoundError:
            pass


class FirebaseUserDoesNotExist(Exception):
    pass


class FirebaseError(Exception):
    pass


class InvalidIdToken(Exception):
    pass


class NoTokenProvided(Exception):
    pass


class NoEntryForUser(Exception):
    pass
