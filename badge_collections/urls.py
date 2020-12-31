from django.urls import path

from badge_collections import views

urlpatterns = [
    path('<uuid>/status', views.status),
    path('<uuid>', views.crud_collection),
    path('', views.collections),
]
