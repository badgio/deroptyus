from django.urls import path

from badge_collections import views

urlpatterns = [
    path('<uuid>/statistics', views.stats_collection),
    path('<uuid>/status', views.status),
    path('<uuid>', views.crud_collection),
    path('', views.collections),
]
