from django.urls import path

from .models import Opportunity
from . import views

api = [
    path("v1/opportunity", views.get_opportunity_list),
    path("v1/opportunity/<uuid:opportunity_id>", views.get_opportunity_list),
    path("v1/subscriber/", views.get_subscriber_list),
    path("v1/subscriber/<uuid:subscriber_id>", views.do_subscriber_update),

    path("v1/artists/", views.get_artist_list),
    path("v1/artists/<uuid:artist_id>", views.artist_view),
    path("v1/artists/<uuid:artist_id>/sms/send", views.sms_send),

    path("v1/notifications/sms/delivery", views.sms_delivery),
    path("v1/notifications/sms/optout", views.sms_optout),
    path("v1/notifications/sms/optin", views.sms_optin),
]

web = [
    path("", views.go_home),
    path("subscribe/<str:organization_slug>/<str:concept_slug>/", views.do_subscribe, name='view-concept'),
    path("subscribe/<str:organization_slug>/<str:concept_slug>", views.do_subscribe, name='view-concept'),
    
    path("invite/<str:opportunity_id>/accept/", views.do_approve, {'action': Opportunity.Status.ACCEPTED}, name='invitation-accept'),
    path("invite/<str:opportunity_id>/skip/", views.do_approve, {'action': Opportunity.Status.SKIP}, name='invitation-re'),
]

urlpatterns = (api + web)
