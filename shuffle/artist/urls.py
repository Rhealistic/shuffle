from django.urls import path

from . import views

urlpatterns = [
    path("", views.subscribe),
    path("subscribe/", views.subscribe),
    path("api/v1/artist/<artist_id>", views.artist_view),
]