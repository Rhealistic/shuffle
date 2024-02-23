from django.contrib import admin

from .models import Artist, Opportunity

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "artist_id",
        "email",
        "phone",
        "instagram",
    ]

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = [
        "subscriber",
        "status",
        "invite_status"
    ]