from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    
    path("santuri/jenga-jungle/", views.subscribe, name='jenga-jungle'),
    path("santuri/jenga-jungle/subscribe/", views.subscribe),

    path("image/search/", views.search_image),
    path("v1/artists", views.artist_list),
    path("v1/artists/<artist_id>", views.artist_view),
]