from django.urls import path, include

urlpatterns = [
    path('', include('authentication.urls')),
    path('v0/locations/', include('location.urls')),
]
