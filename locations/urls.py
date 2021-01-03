from django.urls import path

from . import views

urlpatterns = [
    path('<uuid>/statistics', views.stats_location),
    path('<uuid>', views.crud_location),
    # path('list/', views.filter_location),
    path('', views.locations),
]
