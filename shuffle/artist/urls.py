from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    
    path("<organization_slug>/<concept_slug>/", views.subscribe, name='view-concept'),
    path("<organization_slug>/<concept_slug>/apply/", views.subscribe, name='apply-to-concept'),

    path("v1/artists", views.artist_list),
    path("v1/artists/<artist_id>", views.artist_view),
]