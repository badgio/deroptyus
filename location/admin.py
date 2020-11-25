from django.contrib import admin
from .models import Location, ManagerLocation, SocialMedia

# Register your models here.

admin.site.register(Location)
admin.site.register(SocialMedia)
admin.site.register(ManagerLocation)
