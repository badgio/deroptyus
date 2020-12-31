from django.urls import path

from . import views

urlpatterns = [
    path('<uuid>', views.crud_location),
    # path('list/', views.filter_location),
    path('', views.location_paginator_filter),
]
