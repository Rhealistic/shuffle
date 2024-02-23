from django.urls import path

from . import views

api = [
    path("v1/artists", views.artist_list),
    path("v1/artists/<artist_id>", views.artist_view),
    path("v1/opportunity", views.opportunity_list),
    path("v1/opportunity/<opportunity_id>", views.opportunity_update),
    path("v1/subscriber", views.subscriber_list),
    path("v1/subscriber/<subscriber_id>", views.subscriber_update)
]

web = [
    path("", views.home),
    path("<organization_slug>/<concept_slug>/", views.subscribe, name='view-concept'),
    path("<organization_slug>/<concept_slug>/apply/", views.subscribe, name='apply-to-concept')
]

urlpatterns = (api + web)