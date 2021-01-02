from django.urls import path

from rewards import views

urlpatterns = [
    path('redeem', views.redeem),
    path('<uuid>/statistics', views.stats_reward),
    path('<uuid>', views.crud_reward),
    path('', views.rewards),
]
