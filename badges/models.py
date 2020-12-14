import uuid

from django.db import models
from django.utils import timezone

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
    image = models.ImageField(upload_to='upload/badges/', null=True)
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
        )


class RedeemedBadges(models.Model):
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
