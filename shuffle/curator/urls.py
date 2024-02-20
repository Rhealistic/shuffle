from django.urls import path

from . import views

urlpatterns = [
    path("v1/organizations/", views.organizations),
    path("v1/organizations/<organization_slug>", views.organizations),
    path("v1/<organization_slug>/<concept_slug>/shuffle", views.do_shuffle)
]