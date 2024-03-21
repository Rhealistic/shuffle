from django.urls import path

from shuffle.artist.models import Opportunity
from shuffle.calendar.models import Event

from . import views

urlpatterns = [
    path("v1/organizations", views.get_organizations),
    path("v1/organizations/<str:organization_slug>", views.get_organizations),
    path("v1/organizations/<uuid:organization_id>", views.get_organizations),
    path("v1/concepts", views.get_concepts),
    path("v1/concepts/<uuid:concept_id>", views.get_concepts),
    path("v1/concepts/<uuid:concept_id>/discover", views.do_discover_opportunities),
    path("v1/opportunity/<uuid:opportunity_id>/shuffle/accept", views.accept_shuffle_invite),
    path("v1/shuffle", views.do_shuffle),
    path("v1/shuffle/<uuid:shuffle_id>", views.get_shuffle),
    
    path("v1/concepts/<uuid:concept_id>/event/successful", views.concept_event_complete, {"status": Event.Status.SUCCESSFUL}),
    path("v1/concepts/<uuid:concept_id>/event/cancelled", views.concept_event_complete, {"status": Event.Status.CANCELLED}),
    path("v1/concepts/<uuid:concept_id>/event/rescheduled", views.concept_event_complete, {"status": Event.Status.RESCHEDULED}),
]