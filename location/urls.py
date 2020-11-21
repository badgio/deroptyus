from django.urls import path

from . import views

urlpatterns = [
    path('<uuid>', views.crud_location),
    path('', views.locations),
]
