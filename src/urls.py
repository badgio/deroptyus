from django.contrib import admin
from django.urls import path, include

urlpatterns = [
  path('admin/', admin.site.urls),
  path('v0/locations/', include('locations.urls')),
  path('v0/badges/', include('badges.urls')),
  path('v0/users/', include('users.urls'))
]
