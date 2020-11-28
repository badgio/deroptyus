import uuid

from django.db import models

from users.models import ManagerUser


class Status(models.IntegerChoices):
    APPROVE = 1
    REJECT = 2
    WAIT = 3


class Location(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    image = models.ImageField(upload_to='upload/', null=True)
    status = models.IntegerField(choices=Status.choices, default=3)
    instagram = models.CharField(max_length=255)
    facebook = models.CharField(max_length=255)
    manager = models.ForeignKey(ManagerUser, on_delete=models.CASCADE)
