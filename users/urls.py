from django.urls import path, include

from . import views

urlpatterns = [
    path('appers', views.appers),
]