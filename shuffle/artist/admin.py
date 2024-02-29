from django.contrib import admin

from .models import Artist, Opportunity, Subscriber

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
        "sent_at",
        "closed_at"
    ]


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = [
        "subscriber_id",
        "status",
        "concept",
        "artist",
        "is_subscribed",
        "selection_count",
        "next_performance",
        "last_performance",
    ]