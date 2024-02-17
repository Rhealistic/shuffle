from django.urls import path

from . import views

urlpatterns = [
    path("v1/<curator_slug>/<concept_slug>/shuffle", views.do_shuffle)
]