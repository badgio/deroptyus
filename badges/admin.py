from django.contrib import admin

from .models import Badge, RedeemedBadges

admin.site.register(Badge)
admin.site.register(RedeemedBadges)
