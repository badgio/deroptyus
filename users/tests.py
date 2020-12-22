import pyrebase
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from firebase_admin import auth

from firebase.auth import FirebaseBackend
from firebase.models import FirebaseUser
from .models import AppUser, ManagerUser, PromoterUser, User, AdminUser


class UsersTestCase(TestCase):
    firebase_backend = FirebaseBackend()
    pyrebase_app = pyrebase.initialize_app(settings.PYREBASE_API_KEY)

    def log_in(self, type, email, password):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Signing in without creating user
        if (type == "mobile" and AppUser.objects.filter(email=email).count()) or \
                (type == "managers" and ManagerUser.objects.filter(email=email).count()) or \
                (type == "promoters" and PromoterUser.objects.filter(email=email).count()):
            return self.pyrebase_app.auth().sign_in_with_email_and_password(email, password)["idToken"]

        # Logging the user in the Firebase Console and returning the token for authentication
        client = Client()
        client.post(f'/v0/users/{type}', {
            'email': email,
            'password': password
        }, content_type="application/json")

        return self.pyrebase_app.auth().sign_in_with_email_and_password(email, password)["idToken"]

    def log_in_admin(self, email, password):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Signing in without creating user
        if AdminUser.objects.filter(email=email).count():
            return self.pyrebase_app.auth().sign_in_with_email_and_password(email=email, password=password)["idToken"]

        # Creating Admin user through the command
        call_command('createadmin', email, password)

        # Logging the user in the Firebase Console and returning the token for authentication
        return self.pyrebase_app.auth().sign_in_with_email_and_password(email=email, password=password)["idToken"]

    def log_out(self):
        # Deleting users from the firebase console (as it's not temporary)
        for firebase_user in FirebaseUser.objects.all():
            self.firebase_backend.delete_user_by_id(firebase_user.id)

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

    def test_admin_user_creation(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "admin@test.com"
        password = "test_password"

        # Creating Admin user through the command
        call_command('createadmin', email, password)

        # Testing for manager user creation
        self.assertEqual(AdminUser.objects.filter(email=email).count(), 1)
        admin = AdminUser.objects.get(email=email)

        # Assert a user was created
        user = admin.user
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)

        # Assert a firebase user was created
        firebase_user = FirebaseUser.objects.get(user=user)

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
            'view_location',
            'view_badge',
            'redeem_badge',
            'redeem_reward',
            'view_collection',
            'check_collection_status',
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
            'add_location',
            'view_location',
            'view_badge',
            'view_collection',
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
            'view_location',
            'add_badge',
            'view_badge',
            'add_reward',
            'view_reward',
            'add_collection',
            'view_collection',

        ]
        self.assertSetEqual(Permission.objects.filter(codename__in=promoters_permission_codenames).all(),
                            promoters_group.permissions.all())

        # Making sure every Promoter User is in the Promoter Users group
        for promoter in PromoterUser.objects.all():
            user = User.objects.get(promoter.user)
            self.assertIn(promoters_group, user.groups.all())

    def test_admin_group_permissions(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        # Making sure there is a Permission Group created for the Promoter Users
        admins_group = Group.objects.get(name="admins_permission_group")
        self.assertIsNotNone(admins_group)

        # Making the Group has the correct permissions
        admins_permission_codenames = [
            'view_location',
            'change_location',
            'delete_location',
            'view_badge',
            'change_location',
            'delete_location',
            'add_tag',
            'view_tag',
            'change_tag',
            'delete_tag',
            'view_reward',
            'change_reward',
            'delete_reward',
            'view_collection',
            'change_collection',
            'delete_collection',
        ]
        self.assertSetEqual(Permission.objects.filter(codename__in=admins_permission_codenames).all(),
                            admins_group.permissions.all())

        # Making sure every Promoter User is in the Promoter Users group
        for admin in AdminUser.objects.all():
            user = User.objects.get(admin.user)
            self.assertIn(admins_group, user.groups.all())
