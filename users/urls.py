from django.urls import path

from . import views

urlpatterns = [
    path('mobile', views.appers),
    path('managers', views.managers),
    path('promoters', views.promoters),
]
