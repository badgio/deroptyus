from django.urls import path

from . import views

urlpatterns = [
    path('redeem', views.redeem),
    path('<uuid>', views.crud_badge),
    path('', views.badges),
]
