from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/post/<post_id>/media", views.upload_wordpress_media),
    path("api/v1/site/<site_id>/post", views.create_wordpress_post),

    path("api/v1/site/register", views.register_site),
    path("api/v1/site/<site_id>", views.view_site),
]
