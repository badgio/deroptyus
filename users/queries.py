from django.contrib.auth.models import Group

from firebase.auth import FirebaseBackend
from firebase.models import FirebaseUser
from .models import User, AppUser, PromoterUser, ManagerUser, AdminUser

firebase_backend = FirebaseBackend()


def create_user(email, password, admin):
    # Select auth method based on version
    try:

        firebase_id = firebase_backend.create_user_email_password(email=email, password=password)

    except Exception as e:

        raise FirebaseError(f"Firebase retrieval error: {e}")

    # Checking if a FirebaseUser already exists with the given ID
    try:

        # Getting the FirebaseUser and User
        firebase_user = FirebaseUser.objects.get(pk=firebase_id)
        user = User.objects.get(pk=firebase_user.user_id)

    except FirebaseUser.DoesNotExist:

        # Create entry for a User
        if admin:
            user = User.objects.create_superuser(password=password)
        else:
            user = User.objects.create_user()

        # Creating a FirebaseUser
        firebase_user = FirebaseUser(id=firebase_id, user=user)
        firebase_user.save()

    return user


def create_app_user(app_user_info):
    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(app_user_info.get("email"), app_user_info.get("password"), False)

    try:

        # Checking if there's already an App User associated with the user
        AppUser.objects.get(user_id=user.id)

        raise AppUserExistsError("Email already associated with an App User.")

    except AppUser.DoesNotExist:

        # Creating an AppUser
        app_user = AppUser(email=app_user_info.get("email"),
                           name=app_user_info.get("name"),
                           date_birth=app_user_info.get("date_birth"),
                           country=app_user_info.get("country"),
                           city=app_user_info.get("city"),
                           gender=app_user_info.get("gender"),
                           user=user)
        app_user.save()

        # Set the App User permissions
        try:

            appers_group = Group.objects.get(name='appers_permission_group')

            user.groups.add(appers_group)

        except Exception:

            raise PermissionGroupError("Couldn't get the AppUser's Permission Group")

    return app_user


def create_manager_user(manager_info):
    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(manager_info.get("email"), manager_info.get("password"), False)

    try:

        # Checking if there's already a Manager User associated with the user
        ManagerUser.objects.get(user_id=user.id)

        raise ManagerExistsError("Email already associated with a Manager.")

    except ManagerUser.DoesNotExist:

        # Creating an ManagerUser
        manager_user = ManagerUser(email=manager_info.get("email"), user=user)
        manager_user.save()

        # Set the Manager User permissions
        try:

            managers_group = Group.objects.get(name='managers_permission_group')

            user.groups.add(managers_group)

        except Exception:

            raise PermissionGroupError("Couldn't get the ManagerUser's Permission Group")

    return manager_user


def create_promoter_user(promoter_info):
    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(promoter_info.get("email"), promoter_info.get("password"), False)

    try:

        # Checking if there's already a Promoter User associated with the user
        PromoterUser.objects.get(user_id=user.id)

        raise PromoterExistsError("Email already associated with a Promoter.")

    except PromoterUser.DoesNotExist:

        # Creating a PromoterUser
        promoter_user = PromoterUser(email=promoter_info.get("email"), user=user)
        promoter_user.save()

        # Set the Promoter User permissions
        try:

            promoters_group = Group.objects.get(name='promoters_permission_group')

            user.groups.add(promoters_group)

        except Exception:

            raise PermissionGroupError("Couldn't get the PromoterUser's Permission Group")

    return promoter_user


def create_admin_user(email, password):
    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(email, password, True)

    try:

        # Checking if there's already a Admin User associated with the user
        AdminUser.objects.get(user_id=user.id)

        raise AdminExistsError("Email already associated with an Admin.")

    except AdminUser.DoesNotExist:

        # Creating a AdminUser
        admin_user = AdminUser(email=email, user=user)
        admin_user.save()

        # Set the Admin User permissions
        try:

            admins_group = Group.objects.get(name='admins_permission_group')

            user.groups.add(admins_group)

        except Exception:

            raise PermissionGroupError("Couldn't get the AdminUser's Permission Group")

    return admin_user


class AppUserExistsError(Exception):
    pass


class ManagerExistsError(Exception):
    pass


class PromoterExistsError(Exception):
    pass


class AdminExistsError(Exception):
    pass


class FirebaseError(Exception):
    pass


class PermissionGroupError(Exception):
    pass
