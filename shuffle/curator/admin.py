from django.contrib import admin

from .models import Curator, Concept, Application, Shuffle

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

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "artist",
        "concept",
        "status",
        "created_at"
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