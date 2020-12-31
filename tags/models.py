from django.db import models

import django_filters
from locations.models import Location
from users.models import AdminUser


class Tag(models.Model):
    uid = models.CharField(max_length=255, unique=True, editable=False)
    app_key = models.CharField(max_length=255)
    last_counter = models.IntegerField(default=-1)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    admin = models.ForeignKey(AdminUser, on_delete=models.RESTRICT, editable=False)

    def __str__(self):
        return str(self.uid)


class RedeemedCounters(models.Model):
    counter = models.IntegerField()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class TagFilter(django_filters.FilterSet):
    class Meta:
        model = Tag
        fields = ['uid', 'admin__email', 'location__uuid']
