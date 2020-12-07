from django.urls import path

from . import views

urlpatterns = [
    path('<uid>', views.crud_tag),
    path('', views.tags),
]
