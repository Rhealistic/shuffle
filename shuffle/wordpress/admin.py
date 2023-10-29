from django.contrib import admin

from .models import Site, Post

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = [
        "site_id",
        "website_name",
        "website_url"
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "site",
        "title",
        'status', 
    ]