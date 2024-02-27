from django.urls import path

from .models import Event
from . import views

urlpatterns = [
    path("v1/event/<uuid:event_id>/status/successful", views.do_opportunity_update, {'outcome_status': Event.Status.SUCCESSFUL}),
    path("v1/event/<uuid:event_id>/status/cancelled", views.do_opportunity_update, {'outcome_status': Event.Status.CANCELLED}),
    path("v1/event/<uuid:event_id>/status/rescheduled", views.do_opportunity_update, {'outcome_status': Event.Status.RESCHEDULED}),
    path("v1/event/<uuid:event_id>/status/failed", views.do_opportunity_update, {'outcome_status': Event.Status.FAILED}),
]