from django.contrib import admin
from django.urls import path, include

urlpatterns = [
  path('admin/', admin.site.urls),
  path('v0/locations/', include('location.urls')),
  path('v0/users/', include('users.urls'))
]
