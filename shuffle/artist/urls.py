from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    
    path("santuri/", views.subscribe),
    path("santuri/subscribe/", views.subscribe),

    path("api/v1/artist/<artist_id>", views.artist_view),
]