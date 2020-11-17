from django.urls import path

from . import views

urlpatterns = [
    path('<uuid>', views.crud_badge),
    path('', views.badge),
]