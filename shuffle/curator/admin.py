from django.contrib import admin

from .models import Curator, Concept, Shuffle, Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "organization_id",
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
        "curator_id",
        "name",
        "email",
        "phone",
        "created_at"
    ]

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = [
        "concept_id",
        "title",
        "curator",
        "description",
        "slug",
        "start_date"
    ]

@admin.register(Shuffle)
class ShuffleAdmin(admin.ModelAdmin):
    list_display = [
        "shuffle_id",
        "concept",
        "status",
        "created_at"
    ]