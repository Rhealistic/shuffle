import random
import uuid

from django.db import models


class Event(models.Model):
    event_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)

    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    poster = models.URLField(max_length=500, null=True, blank=True)
    event_date = models.DateTimeField()

    concept = models.ForeignKey('curator.Concept', models.SET_NULL, null=True)
    venue = models.ForeignKey('curator.Venue', models.SET_NULL, related_name='venues', null=True)
    opportunity = models.ForeignKey('artist.Opportunity', models.SET_NULL, null=True)


    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

