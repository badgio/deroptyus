from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from firebase_admin import auth

from firebase.auth import FirebaseBackend
from firebase.models import FirebaseUser
from .models import AppUser, ManagerUser, PromoterUser, User


# Create your tests here.

class UsersTestCase(TestCase):
    firebase_backend = FirebaseBackend()

    def test_app_user_creation(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "app_user@test.com"
        password = "test_password"
        name = "app_user"
        date_birth = "2000-02-20"
        gender = "female"
        country = "portugal"
        city = "braga"

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
        }, content_type="application/json")

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
        }, content_type="application/json")
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_manager_user_creation(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "manager@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a manager
        response = client.post('/v0/users/managers', {'email': email, 'password': password},
                               content_type="application/json")

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
        response = client.post('/v0/users/managers', {'email': email, 'password': password},
                               content_type="application/json")
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_promoter_user_creation(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "promoter@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a promoter
        response = client.post('/v0/users/promoters', {'email': email, 'password': password},
                               content_type="application/json")

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
        response = client.post('/v0/users/promoters', {'email': email, 'password': password},
                               content_type="application/json")
        self.assertGreaterEqual(response.status_code, 400)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_manager_promoter_user_creation(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "manager_promoter@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create a promoter
        response = client.post('/v0/users/managers', {'email': email, 'password': password},
                               content_type="application/json")

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
        response = client.post('/v0/users/promoters', {'email': email, 'password': password},
                               content_type="application/json")
        self.assertGreaterEqual(response.status_code, 201)
        promoter = PromoterUser.objects.get(email=email)

        # Testing that the promoter and manager share the user ID
        self.assertEqual(promoter.user_id, manager.user_id)

        # Removing the user from the firebase DB (as it's not temporary)
        auth.delete_user(firebase_user.id, app=self.firebase_backend.app)

    def test_apper_group_permissions(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Making sure there is a Permission Group created for the App Users
        appers_group = Group.objects.get(name="appers_permission_group")
        self.assertIsNotNone(appers_group)

        # Making the Group has the correct permissions
        appers_permission_codenames = [
            'change_appuser',
            'view_appuser',
            'delete_appuser'
        ]
        self.assertSetEqual(Permission.objects.filter(codename__in=appers_permission_codenames).all(),
                            appers_group.permissions.all())

        # Making sure every App User is in the App Users group
        for apper in AppUser.objects.all():
            user = User.objects.get(apper.user)
            self.assertIn(appers_group, user.groups.all())

    def test_manager_group_permissions(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Making sure there is a Permission Group created for the Manager Users
        managers_group = Group.objects.get(name="managers_permission_group")
        self.assertIsNotNone(managers_group)

        # Making the Group has the correct permissions
        managers_permission_codenames = [
            'change_manageruser',
            'view_manageruser',
            'delete_manageruser'
        ]
        self.assertSetEqual(Permission.objects.filter(codename__in=managers_permission_codenames).all(),
                            managers_group.permissions.all())

        # Making sure every Manager User is in the Manager Users group
        for manager in ManagerUser.objects.all():
            user = User.objects.get(manager.user)
            self.assertIn(managers_group, user.groups.all())

    def test_promoter_group_permissions(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Making sure there is a Permission Group created for the Promoter Users
        promoters_group = Group.objects.get(name="promoters_permission_group")
        self.assertIsNotNone(promoters_group)

        # Making the Group has the correct permissions
        promoters_permission_codenames = [
            'change_promoteruser',
            'view_promoteruser',
            'delete_promoteruser'
        ]
        self.assertSetEqual(Permission.objects.filter(codename__in=promoters_permission_codenames).all(),
                            promoters_group.permissions.all())

        # Making sure every Promoter User is in the Promoter Users group
        for promoter in PromoterUser.objects.all():
            user = User.objects.get(promoter.user)
            self.assertIn(promoters_group, user.groups.all())
