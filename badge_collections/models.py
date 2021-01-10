import uuid

import django_filters
from django.db import models
from django.utils import timezone

from badges.models import Badge, RedeemedBadge
from rewards.models import Reward
from users.models import PromoterUser, AppUser
import sys


class Status(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending Approval"


class Collection(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.TextField(null=True)
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

    def badge_filter(self, queryset, name, value):
        collection_uuid_with_badges = CollectionBadge.objects.filter(badge__uuid=value).\
            values_list('collection__uuid', flat=True)
        return queryset.filter(**{
            'uuid__in': collection_uuid_with_badges,
        })


    def localtion_filter(self, queryset, name, value):
        badge_uuid_with_location = Badge.objects.filter(location__uuid=value).\
            values_list('uuid', flat=True)
        collection_uuid_with_badges = CollectionBadge.objects.\
            filter(badge__uuid__in=badge_uuid_with_location).\
            values_list('collection__uuid', flat=True)
        print(collection_uuid_with_badges, file=sys.stderr)
        return queryset.filter(**{
            'uuid__in': collection_uuid_with_badges,
        })

    def completed_filter(self, queryset, name, value):

        # Getting app user that's redeeming the badge
        try:
            apper = AppUser.objects.get(email__exact=value)
        except AppUser.DoesNotExist:
            return queryset.none()

        collections_completed = []
        # Getting collection with UUID
        for collection in Collection.objects.all():
            badges_in_collection = CollectionBadge.objects.filter(collection=collection).values_list('badge', flat=True)
            badges_in_collection_collected = RedeemedBadge.objects.filter(badge__in=badges_in_collection, app_user=apper)
            
            if badges_in_collection.count() == badges_in_collection_collected.count():
                collections_completed += [collection.uuid]
        
        return queryset.filter(**{
            'uuid__in': collections_completed,
        })

    completed_by = django_filters.CharFilter(method='completed_filter')
    location = django_filters.UUIDFilter(method='localtion_filter')
    badge = django_filters.UUIDFilter(method='badge_filter')
    start_date__lt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lt')
    start_date__gt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gt')
    end_date__lt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lt')
    end_date__gt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='gt')
    created_by = django_filters.CharFilter(field_name='promoter__email')

    class Meta:
        model = Collection
        fields = ['uuid', 'name', 'description', 'start_date', 'end_date', 'reward__uuid', 'status']



class CollectionBadge(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
