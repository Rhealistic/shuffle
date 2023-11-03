from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/site/<site_id>/notify-indexer", views.notify_indexer),
]
