from django.urls import path

from .models import Opportunity
from . import views

api = [
    path("v1/artists/", views.get_artist_list),
    path("v1/artists/<uuid:artist_id>", views.artist_view),

    path("v1/opportunity", views.get_opportunity_list),

    path("v1/opportunity/<uuid:opportunity_id>/invite/accepted", views.do_opportunity_update, {'invite_status': Opportunity.InviteStatus.ACCEPTED}),
    path("v1/opportunity/<uuid:opportunity_id>/invite/rejected", views.do_opportunity_update, {'invite_status': Opportunity.InviteStatus.SKIP}),
    path("v1/opportunity/<uuid:opportunity_id>/invite/expired", views.do_opportunity_update, {'invite_status': Opportunity.InviteStatus.EXPIRED}),
    path("v1/opportunity/<uuid:opportunity_id>/outcome/successful", views.do_opportunity_update, {'outcome_status': Opportunity.OutcomeStatus.SUCCESSFUL}),
    path("v1/opportunity/<uuid:opportunity_id>/outcome/cancelled", views.do_opportunity_update, {'outcome_status': Opportunity.OutcomeStatus.CANCELLED}),
    path("v1/opportunity/<uuid:opportunity_id>/outcome/postponed", views.do_opportunity_update, {'outcome_status': Opportunity.OutcomeStatus.POSTPONED}),
    
    path("v1/opportunity/<uuid:opportunity_id>", views.do_opportunity_update),
    path("v1/subscriber/", views.get_subscriber_list),
    path("v1/subscriber/<uuid:subscriber_id>", views.do_subscriber_update)
]

web = [
    path("", views.go_home),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/", views.do_subscribe, name='view-concept'),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/apply/", views.do_subscribe, name='apply-to-concept')
]

urlpatterns = (api + web)