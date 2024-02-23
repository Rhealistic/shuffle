from django.urls import path

from . import views

urlpatterns = [
    path("v1/organizations", views.get_organizations),
    path("v1/organizations/<str:organization_slug>", views.get_organizations),
    path("v1/organizations/<uuid:organization_id>", views.get_organizations),
    path("v1/concepts", views.get_concepts),
    path("v1/concepts/<uuid:concept_id>", views.get_concepts),

    path("v1/shuffle", views.do_shuffle),
    path("v1/shuffle/<uuid:shuffle_id>", views.get_or_update_shuffle),
    path("v1/shuffle/<uuid:shuffle_id>/reshuffle", views.do_reshuffle),
]