from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v0/locations/', include('locations.urls')),
    path('v0/badges/', include('badges.urls')),
    path('v0/collections/', include('badge_collections.urls')),
    path('v0/tags/', include('tags.urls')),
    path('v0/rewards/', include('rewards.urls')),
    path('v0/users/', include('users.urls'))
]
