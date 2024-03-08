from django.contrib import admin

from .models import Config, Curator, Concept, Shuffle, Organization

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
        "organization",
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
        "pick",
        "retries",
        "status",
        "start_time",
        "closed_at",
        "created_at"
    ]

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = [
        "config_id",
        "key",
        "value",
        "type",
    ]