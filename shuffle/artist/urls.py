from django.urls import path

from .models import Opportunity
from . import views

api = [
    path("v1/artists/", views.get_artist_list),
    path("v1/artists/<uuid:artist_id>", views.artist_view),

    path("v1/opportunity", views.get_opportunity_list),

    path("v1/opportunity/<uuid:opportunity_id>/invite/accepted", views.do_opportunity_update, {'status': Opportunity.Status.ACCEPTED}),
    path("v1/opportunity/<uuid:opportunity_id>/invite/rejected", views.do_opportunity_update, {'status': Opportunity.Status.SKIP}),
    path("v1/opportunity/<uuid:opportunity_id>/invite/expired", views.do_opportunity_update, {'status': Opportunity.Status.EXPIRED}),
    path("v1/opportunity/<uuid:opportunity_id>", views.do_opportunity_update),
    
    path("v1/subscriber/", views.get_subscriber_list),
    path("v1/subscriber/<uuid:subscriber_id>", views.do_subscriber_update)
]

web = [
    path("", views.go_home),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/", views.do_subscribe, name='view-concept')
]

urlpatterns = (api + web)
