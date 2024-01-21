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
        "opportunity_status",
        "invite_status",
        "performance_count",
    ]

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = [
        "artist",
        "concept"
    ]