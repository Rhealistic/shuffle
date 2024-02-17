import random
from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)
    logo = models.URLField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

class Curator(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True)

    organization = models.ForeignKey('Organization', models.SET_NULL, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)


class Concept(models.Model):
    title = models.CharField(max_length=150)
    curator = models.ForeignKey('Curator', models.SET_NULL, null=True)
    description = models.CharField(max_length=500)

    slug = models.SlugField(max_length=75, null=True)
    poster = models.URLField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)


class Shuffle(models.Model):
    concept = models.ForeignKey('Concept', models.SET_NULL, null=True)

    NORMAL = 0
    RESHUFFLE = 1
    TYPE = (
        (NORMAL, "Normal"),
        (RESHUFFLE, "Reshuffle"),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE, null=True, default=0)

    chosen = models.ForeignKey("artist.Artist", models.SET_NULL, null=True)

    last_shuffle = models.DateTimeField()
    next_shuffle = models.DateTimeField()

    start_date = models.DateTimeField(null=True)
    end_date   = models.DateTimeField(null=True)

    STATUS = (
        (0, "Started"),
        (1, "In Progress"),
        (2, "Invite Sent"),
        (3, "Accepted"),
        (4, "Reshuffle"),
        (5, "Complete")
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=0)
    retries = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
        