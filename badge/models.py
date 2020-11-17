from django.db import models
import uuid
from location.models import Location, Status


class Badge(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    nfc_tag = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices, default=3)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
