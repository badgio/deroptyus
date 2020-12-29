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
                           user=user)

        if "name" in app_user_info:
            app_user.name = app_user_info.get("name")
        if "date_birth" in app_user_info:
            app_user.date_birth = app_user_info.get("date_birth")
        if "country" in app_user_info:
            app_user.country = app_user_info.get("country")
        if "city" in app_user_info:
            app_user.city = app_user_info.get("city")
        if "gender" in app_user_info:
            app_user.gender = app_user_info.get("gender")

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


def get_app_user(user):
    try:
        return AppUser.objects.get(user=user)
    except AppUser.DoesNotExist:
        return None


def get_manager_user(user):
    try:
        return ManagerUser.objects.get(user=user)
    except ManagerUser.DoesNotExist:
        return None


def get_promoter_user(user):
    try:
        return PromoterUser.objects.get(user=user)
    except PromoterUser.DoesNotExist:
        return None


def get_admin_user(user):
    try:
        return AdminUser.objects.get(user=user)
    except AdminUser.DoesNotExist:
        return None


def patch_user(user_data, user):
    try:
        firebase_user = FirebaseUser.objects.get(user=user)
    except FirebaseUser.DoesNotExist:
        raise FirebaseUserDoesNotExist()

    if "email" in user_data:
        # Setting email for change
        user_data["mobile_info"]["email"] = user_data.get("email")
        user_data["manager_info"]["email"] = user_data.get("email")
        user_data["promoter_info"]["email"] = user_data.get("email")
        user_data["admin_info"]["email"] = user_data.get("email")
        # Changing email in Firebase
        firebase_backend.change_users_email(uid=firebase_user.id, email=user_data.get("email"))

    if "password" in user_data:
        # Changing password in Firebase
        firebase_backend.change_users_password(uid=firebase_user.id, password=user_data.get("password"))

    if "mobile_info" in user_data:
        patch_app_user(user_data["mobile_info"], user)

    if "manager_info" in user_data:
        patch_manager_user(user_data["manager_info"], user)

    if "promoter_info" in user_data:
        patch_promoter_user(user_data["promoter_info"], user)

    if "admin_info" in user_data:
        patch_admin_user(user_data["admin_info"], user)


def patch_app_user(app_user_info, user):
    # Getting AppUser
    app_user = get_app_user(user)

    if not app_user:
        return

    if "email" in app_user_info:
        app_user.email = app_user_info.get("email")
    if "name" in app_user_info:
        app_user.name = app_user_info.get("name")
    if "date_birth" in app_user_info:
        app_user.date_birth = app_user_info.get("date_birth")
    if "country" in app_user_info:
        app_user.country = app_user_info.get("country")
    if "city" in app_user_info:
        app_user.city = app_user_info.get("city")
    if "gender" in app_user_info:
        app_user.gender = app_user_info.get("gender")

    app_user.save()


def patch_manager_user(manager_user_info, user):
    # Getting AppUser
    manager_user = get_manager_user(user)

    if not manager_user:
        return

    if "email" in manager_user_info:
        manager_user.email = manager_user_info.get("email")

    manager_user.save()


def patch_promoter_user(promoter_user_info, user):
    # Getting AppUser
    promoter_user = get_promoter_user(user)

    if not promoter_user:
        return

    if "email" in promoter_user_info:
        promoter_user.email = promoter_user_info.get("email")

    promoter_user.save()


def patch_admin_user(admin_user_info, user):
    # Getting AppUser
    admin_user = get_admin_user(user)

    if not admin_user:
        return

    if "email" in admin_user_info:
        admin_user.email = admin_user_info.get("email")

    admin_user.save()


def delete_user(user):
    # Getting FirebaseUser
    try:
        firebase_user = FirebaseUser.objects.get(user=user)
    except FirebaseUser.DoesNotExist:
        raise FirebaseUserDoesNotExist()

    # Deleting the user in the Firebase Console
    firebase_backend.delete_user(uid=firebase_user.id)
    # Deleting the User
    user.delete()


def get_str_by_app_user_pk(pk):
    return str(AppUser.objects.get(pk=pk))


def get_str_by_manager_pk(pk):
    return str(ManagerUser.objects.get(pk=pk))


def get_str_by_promoter_pk(pk):
    return str(PromoterUser.objects.get(pk=pk))


def get_str_by_admin_pk(pk):
    return str(AdminUser.objects.get(pk=pk))


class AppUserExistsError(Exception):
    pass


class ManagerExistsError(Exception):
    pass


class PromoterExistsError(Exception):
    pass


class AdminExistsError(Exception):
    pass


class FirebaseUserDoesNotExist(Exception):
    pass


class FirebaseError(Exception):
    pass


class PermissionGroupError(Exception):
    pass
