from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, **extra_fields):

        user = self.model(**extra_fields)

        return user

    def create_superuser(self, password, **extra_fields):

        user = self.model(**extra_fields)
        user.set_password(password)

        user.is_staff     = True
        user.is_superuser = True
        user.is_active    = True

        user.save()

        return user