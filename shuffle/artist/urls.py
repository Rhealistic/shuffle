from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    
    path("santuri/jenga-jungle/", views.subscribe, name='jenga-jungle'),
    path("santuri/jenga-jungle/subscribe/", views.subscribe),

    path("image/search/", views.search_image),
    path("api/v1/artists/<artist_id>", views.artist_view),
]