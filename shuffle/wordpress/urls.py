from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/wp/<site_id>/post", views.create_wordpress_post),
    path("api/v1/wp/post/<post_id>/media", views.upload_wordpress_media),
]
