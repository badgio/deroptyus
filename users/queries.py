from .models import User, AppUser, PromoterUser, ManagerUser
from firebase.models import FirebaseUser
from firebase.auth import FirebaseBackend

firebase_backend = FirebaseBackend()

def create_user (email, password):

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
        user = User()
        user.save()

        # Creating a FirebaseUser
        firebase_user = FirebaseUser(id=firebase_id, user=user)
        firebase_user.save()

    return user

def create_app_user (email, password, name, date_birth, country, city, gender):

    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(email, password)

    try:

        # Checking if there's already an App User associated with the user
        AppUser.objects.get(user_id=user.id)

        raise AppUserExistsError("Email already associated with an App User.")

    except AppUser.DoesNotExist:

        # Creating an AppUser
        app_user = AppUser(email=email, name=name, date_birth=date_birth, country=country, city=city, gender=gender, user=user)
        app_user.save()

        # Set the App User permissions

    return app_user

def create_manager_user (email, password):

    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(email, password)

    try:

        # Checking if there's already an App User associated with the user
        ManagerUser.objects.get(user_id=user.id)

        raise ManagerExistsError("Email already associated with a Manager.")

    except ManagerUser.DoesNotExist:

        # Creating an ManagerUser
        manager_user = ManagerUser(email=email, user=user)
        manager_user.save()

        # Set the Manager User permissions

    return manager_user

def create_promoter_user (email, password):

    # Creating a user in the firebase console and creating the FirebaseUser and User models
    user = create_user(email, password)

    try:

        # Checking if there's already an App User associated with the user
        PromoterUser.objects.get(user_id=user.id)

        raise PromoterExistsError("Email already associated with a Promoter.")

    except PromoterUser.DoesNotExist:

        # Creating a PromoterUser
        promoter_user = PromoterUser(email=email, user=user)
        promoter_user.save()

        # Set the Promoter User permissions

    return promoter_user

class AppUserExistsError (Exception):
    pass

class FirebaseError (Exception):
    pass

class ManagerExistsError(Exception):
    pass

class PromoterExistsError(Exception):
    pass
