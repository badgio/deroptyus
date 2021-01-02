from django.urls import path

from . import views

urlpatterns = [
    path('redeem', views.redeem),
    path('<uuid>/statistics', views.stats_badge),
    path('<uuid>', views.crud_badge),
    path('', views.badges),
]
