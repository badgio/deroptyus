import uuid

import django_filters
from django.db import models
from django.utils import timezone

from badges.models import Badge
from rewards.models import Reward
from users.models import PromoterUser


class Status(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending Approval"


class Collection(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='upload/collections/', null=True)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True)
    promoter = models.ForeignKey(PromoterUser, on_delete=models.RESTRICT)
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        permissions = (
            ('check_collection_status', 'Can check completion status of a Collection'),
            ('view_stats', 'Can view statistics for a Collection'),
        )


class CollectionFilter(django_filters.FilterSet):
    start_date__lt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lt')
    start_date__gt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gt')
    end_date__lt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lt')
    end_date__gt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='gt')

    class Meta:
        model = Collection
        fields = ['uuid', 'name', 'description', 'start_date', 'end_date', 'promoter__email', 'reward__uuid', 'status']


class CollectionBadge(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
