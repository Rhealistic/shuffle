from django.contrib import admin

from .models import Event

@admin.register(Event)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'event_id',
        'title',
        'description',
        'event_date',
        'concept',
        'venue',
    ]
