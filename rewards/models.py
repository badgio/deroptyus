import uuid

from django.db import models

from locations.models import Location
from users.models import AppUser, PromoterUser


class Status(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending Approval"


class Reward(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='upload/rewards/', null=True)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    time_redeem = models.IntegerField(null=True)  # Time to redeem in seconds
    promoter = models.ForeignKey(PromoterUser, on_delete=models.RESTRICT)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        permissions = (
            ('redeem_reward', 'Can redeem Reward'),
            ('view_stats', 'Can view statistics for a Reward'),
        )


class RedeemedReward(models.Model):
    reward_code = models.CharField(max_length=6, primary_key=True)
    time_awarded = models.DateTimeField(auto_now_add=True, editable=False)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT)
    redeemed = models.BooleanField(default=False)
