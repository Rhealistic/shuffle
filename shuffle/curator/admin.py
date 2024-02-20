from django.contrib import admin

from .models import Curator, Concept, Shuffle, Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "email",
        "phone",
        "logo",
        "created_at"
    ]


@admin.register(Curator)
class CuratorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "phone",
        "created_at"
    ]

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "curator",
        "description",
        "slug",
        "poster",
        "date"
    ]

@admin.register(Shuffle)
class ShuffleAdmin(admin.ModelAdmin):
    list_display = [
        "concept",
        "last_shuffle",
        "next_shuffle",
        "status",
        "created_at"
    ]