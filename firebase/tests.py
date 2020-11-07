from django.test import TestCase
from .auth import FirebaseBackend
from firebase_admin import auth

# Create your tests here.

class FirebaseTestCase (TestCase):

    firebase_backend = FirebaseBackend()

    def test_creation (self):

        email = "email@test.com"
        password = "test_password"

        # Creating the user
        uid = self.firebase_backend.create_user_email_password(email, password)

        # Checking if user exists
        user = auth.get_user_by_email(email, app=self.firebase_backend.app)

        # Checking if uid given on creation matches the stored uid in firebase
        self.assertEqual(user.uid, uid)

        # Removing the user
        auth.delete_user(uid, app=self.firebase_backend.app)