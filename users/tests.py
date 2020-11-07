from django.test import TestCase
from django.test import Client
from firebase_admin import auth
from .models import User, AppUser
from firebase.models import FirebaseUser
from firebase.auth import FirebaseBackend

# Create your tests here.

class TestCase (TestCase):

    firebase_backend = FirebaseBackend()

    def test_app_user_creation (self):

        email = "email@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create an app user
        response = client.post('/users/appers', {'email': email, 'password': password})

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 200)

        # Testing for app user creation
        self.assertEqual(AppUser.objects.filter(email=email).count(), 1)
        app_user = AppUser.objects.get(email=email)

        # Assert a user was created
        user_id = app_user.user_id
        self.assertIsNotNone(user_id)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user_id=user_id)

        # Assert you can't create another app user with same email
        response = client.post('/users/appers', {'email': email, 'password': password})
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)