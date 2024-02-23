from django.urls import path

from . import views

api = [
    path("v1/artists/", views.artist_list),
    path("v1/artists/<uuid:artist_id>", views.artist_view),
    path("v1/opportunity", views.opportunity_list),
    path("v1/opportunity/<uuid:opportunity_id>", views.opportunity_update),
    path("v1/subscriber/", views.subscriber_list),
    path("v1/subscriber/<uuid:subscriber_id>", views.subscriber_update)
]

web = [
    path("", views.home),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/", views.subscribe, name='view-concept'),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/apply/", views.subscribe, name='apply-to-concept')
]

urlpatterns = (api + web)