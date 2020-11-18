from django.conf import settings
from django.db import models


# Create your models here.

class FirebaseUser(models.Model):
    id = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.id
