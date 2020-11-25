from django.db import models
import uuid


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


class SocialMedia(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    social_media = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
