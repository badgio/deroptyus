import uuid

from django.db import models
from django.utils import timezone

import django_filters
from locations.models import Location
from users.models import AppUser, PromoterUser


class Status(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending Approval"


class Badge(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.TextField(null=True)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True)
    location = models.ForeignKey(Location, on_delete=models.RESTRICT)
    promoter = models.ForeignKey(PromoterUser, on_delete=models.RESTRICT)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        permissions = (
            ('redeem_badge', 'Can redeem Badge'),
            ('view_stats', 'Can view statistics for a Badge'),
        )


class RedeemedBadge(models.Model):
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    time_redeemed = models.DateTimeField(auto_now_add=True)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)


class BadgeFilter(django_filters.FilterSet):

    def collected_filter(self, queryset, name, value):

        # Getting app user that's redeeming the badge
        try:
            apper = AppUser.objects.get(email__exact=value)
        except AppUser.DoesNotExist:
            return queryset.none()

        badges_collected = RedeemedBadge.objects.filter(app_user=apper).values_list('badge__uuid', flat=True)
        
        return queryset.filter(**{
            'uuid__in': badges_collected,
        })

    collected_by = django_filters.CharFilter(method='collected_filter')
    start_date__lt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lt')
    start_date__gt = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gt')
    end_date__lt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lt')
    end_date__gt = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='gt')
    created_by = django_filters.CharFilter(field_name='promoter__email')

    class Meta:
        model = Badge
        fields = ['uuid', 'name', 'description', 'status', 'start_date',
                  'end_date', 'location__uuid']
