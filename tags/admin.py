from django.contrib import admin

from .models import Tag, RedeemedCounters

admin.site.register(Tag)
admin.site.register(RedeemedCounters)
