from .models import User, AppUser
from firebase.models import FirebaseUser
from firebase.auth import FirebaseBackend

firebase_backend = FirebaseBackend()

def create_app_user (email, password):

    if AppUser.objects.filter(email=email).count() != 0:

        raise AppUserExistsError("Email already in use.")

    # Select auth method based on version
    try:

        firebase_id = firebase_backend.create_user_email_password(email=email, password=password)

    except Exception as e:

        raise FirebaseError(f"Firebase retrieval error: {e}")

    # Create entry for the user token
    user = User()
    user.save()

    # Creating "Auth" User
    firebase_user = FirebaseUser(id=firebase_id, user=user)
    firebase_user.save()

    # Set the app user permissions

    # Create the actual user
    app_user = AppUser(email=email, user=user)
    app_user.save()

    return app_user

class AppUserExistsError (Exception):
    pass

class FirebaseError (Exception):
    pass