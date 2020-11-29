import uuid
from django.db import models
from users.models import PromoterUser
from locations.models import Location


class Status(models.IntegerChoices):
    APPROVE = 1
    REJECT = 2
    WAIT = 3


class Badge(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='upload/badges/', null=True)
    status = models.IntegerField(choices=Status.choices, default=3)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    manager = models.ForeignKey(PromoterUser, on_delete=models.CASCADE)
