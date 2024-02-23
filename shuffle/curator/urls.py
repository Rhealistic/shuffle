from django.urls import path

from . import views

urlpatterns = [
    path("v1/organizations", views.get_organizations),
    path("v1/organizations/<organization_slug>", views.get_organizations),
    path("v1/shuffle", views.do_shuffle),
    path("v1/shuffle/<shuffle_id>", views.get_or_update_shuffle),
    path("v1/shuffle/<shuffle_id>/reshuffle", views.do_reshuffle),
]