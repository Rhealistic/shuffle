import random
import uuid

from django.db import models


class Venue(models.Model):
    venue_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=75, null=True)

    point = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
            return self.name


