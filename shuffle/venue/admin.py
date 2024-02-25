from django.contrib import admin

from .models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = [
        'venue_id',
        'name',
        'slug',
        'point',
    ]
