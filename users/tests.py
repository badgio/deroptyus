from django.test import TestCase
from django.test import Client
from firebase_admin import auth
from .models import User, AppUser, ManagerUser, PromoterUser
from firebase.models import FirebaseUser
from firebase.auth import FirebaseBackend

# Create your tests here.

class TestCase (TestCase):

    firebase_backend = FirebaseBackend()

    def test_app_user_creation (self):

        email       = "app_user@test.com"
        password    = "test_password"
        name        = "app_user"
        date_birth  = "2000-02-20"
        gender      = "female"
        country     = "portugal"
        city        = "braga"

        client = Client()

        # Sending request to create an app user
        response = client.post('/v0/users/mobile', {
            'email': email,
            'password': password,
            'name': name,
            'date_birth': date_birth,
            'gender': gender,
            'country': country,
            'city': city
        })

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 201)

        # Testing for app user creation
        self.assertEqual(AppUser.objects.filter(email=email).count(), 1)
        app_user = AppUser.objects.get(email=email)

        # Assert a user was created
        user_id = app_user.user_id
        self.assertIsNotNone(user_id)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user_id=user_id)

        # Assert you can't create another app user with same email
        response = client.post('/v0/users/mobile', {
            'email': email,
            'password': password,
            'name': name,
            'date_birth': date_birth,
            'gender': gender,
            'country': country,
            'city': city
        })
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_manager_user_creation (self):

        email = "manager@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a manager
        response = client.post('/v0/users/managers', {'email': email, 'password': password})

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 201)

        # Testing for manager user creation
        self.assertEqual(ManagerUser.objects.filter(email=email).count(), 1)
        manager = ManagerUser.objects.get(email=email)

        # Assert a user was created
        user_id = manager.user_id
        self.assertIsNotNone(user_id)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user_id=user_id)

        # Assert you can't create another manager user with same email
        response = client.post('/v0/users/managers', {'email': email, 'password': password})
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_promoter_user_creation (self):

        email = "promoter@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a promoter
        response = client.post('/v0/users/promoters', {'email': email, 'password': password})

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 201)

        # Testing for promoter user creation
        self.assertEqual(PromoterUser.objects.filter(email=email).count(), 1)
        promoter = PromoterUser.objects.get(email=email)

        # Assert a user was created
        user_id = promoter.user_id
        self.assertIsNotNone(user_id)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user_id=user_id)

        # Assert you can't create another promoter user with same email
        response = client.post('/v0/users/promoters', {'email': email, 'password': password})
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_manager_promoter_user_creation (self):

        email = "manager_promoter@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a promoter
        response = client.post('/v0/users/managers', {'email': email, 'password': password})

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 201)

        # Testing for manager user creation
        self.assertEqual(ManagerUser.objects.filter(email=email).count(), 1)
        manager = ManagerUser.objects.get(email=email)

        # Assert a user was created
        user_id = manager.user_id
        self.assertIsNotNone(user_id)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user_id=user_id)

        # Assert you can create a promoter user with same email
        response = client.post('/v0/users/promoters', {'email': email, 'password': password})
        self.assertGreaterEqual(response.status_code, 201)
        promoter = PromoterUser.objects.get(email=email)

        # Testing that the promoter and manager share the user ID
        self.assertEqual(promoter.user_id, manager.user_id)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)
