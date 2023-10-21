from django.urls import path

from . import views

urlpatterns = [
    path("", views.subscribe),
    path("subscribe/", views.subscribe),
]