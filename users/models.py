import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from .managers import UserManager

# Create your models here.
class User(AbstractUser):

    uuid = models.CharField(primary_key=True, max_length=255, default=str(uuid.uuid4()), editable=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    email = None
    username = None
    last_login = None
    first_name = None
    last_name = None
    date_joined = None

    USERNAME_FIELD = 'uuid'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):

        return self.id

class AppUser(models.Model):

    email       = models.EmailField(max_length=255, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):

        return self.email