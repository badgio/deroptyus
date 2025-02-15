import uuid

import django_filters
from django.db import models

from users.models import ManagerUser


class Status(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending Approval"


class Location(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    image = models.TextField(null=True)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    instagram = models.CharField(max_length=255, null=True)
    facebook = models.CharField(max_length=255, null=True)
    twitter = models.CharField(max_length=255, null=True)
    manager = models.ForeignKey(ManagerUser, on_delete=models.RESTRICT)

    class Meta:
        permissions = (
            ('view_stats', 'Can view statistics for a location'),
        )

    def __str__(self):
        return str(self.uuid)


class LocationFilter(django_filters.FilterSet):
    created_by = django_filters.CharFilter(field_name='manager__email')

    class Meta:
        model = Location
        fields = ['uuid', 'status', 'name', 'website', 'latitude',
                  'longitude', 'instagram', 'facebook', 'twitter']
