from django.urls import path, include

from . import views

urlpatterns = [
    path('mobile', views.appers),
]
