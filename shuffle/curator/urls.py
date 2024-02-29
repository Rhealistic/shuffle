from django.urls import path

from shuffle.artist.models import Opportunity

from . import views

urlpatterns = [
    path("v1/organizations", views.get_organizations),
    path("v1/organizations/<str:organization_slug>", views.get_organizations),
    path("v1/organizations/<uuid:organization_id>", views.get_organizations),
    path("v1/concepts", views.get_concepts),
    path("v1/concepts/<uuid:concept_id>", views.get_concepts),
    path("v1/concepts/<uuid:concept_id>/discover", views.do_discover_opportunities),
    path("v1/concepts/<uuid:concept_id>/shuffle", views.do_shuffle),
    path("v1/opportunity/<uuid:opportunity_id>/shuffle/accept", views.accept_shuffle_invite),
    path("v1/opportunity/<uuid:opportunity_id>/shuffle/expired", views.do_reshuffle, {'opportunity_status': Opportunity.Status.EXPIRED}),
    path("v1/opportunity/<uuid:opportunity_id>/shuffle/skip", views.do_reshuffle, {'opportunity_status': Opportunity.Status.SKIP}),
    path("v1/shuffle/<uuid:shuffle_id>", views.get_shuffle),
]