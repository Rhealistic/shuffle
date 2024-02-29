import random
import uuid

from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True)

    organization_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)
    logo = models.URLField(max_length=500, null=True, blank=True)

    is_active = models.BooleanField(default=True, null=True)

    last_shuffle = models.DateTimeField(null=True)
    next_shuffle = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Curator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    curator_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)
    organization = models.ForeignKey('Organization', models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Concept(models.Model):
    class RecurrenceType(models.IntegerChoices):
        DAILY = 0, "Daily"
        WEEKLY = 1, "Weekly"
        MONTHLY = 2, "Monthly"

    concept_id = models.UUIDField(max_length=30, default = uuid.uuid4)
    curator = models.ForeignKey('Curator', models.SET_NULL, null=True)

    slug = models.SlugField(max_length=75, null=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500)

    start_date = models.DateTimeField(auto_now_add=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.PositiveSmallIntegerField(choices=RecurrenceType.choices, null=True)

    times_per_week = models.PositiveSmallIntegerField(blank=True, null=True)
    times_per_month = models.PositiveSmallIntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title


class Shuffle(models.Model):

    class ShuffleStatus(models.IntegerChoices):
        STARTED = 0, "Started"
        IN_PROGRESS = 1, "In Progress"
        INVITE_SENT = 2, "Invite Sent"
        ACCEPTED = 3, "Accepted"
        RESHUFFLE = 4, "Reshuffle"
        COMPLETE = 5, "Complete"
        FAILED = 6, "Failed"
    
    shuffle_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)
    concept = models.ForeignKey('Concept', models.SET_NULL, null=True)

    start_date = models.DateTimeField(null=True)
    closed_at   = models.DateTimeField(null=True)

    status = models.PositiveSmallIntegerField(choices=ShuffleStatus.choices, default=ShuffleStatus.STARTED)
    retries = models.PositiveSmallIntegerField(default=0)
    pick = models.ForeignKey("artist.Artist", models.SET_NULL, null=True)

    previous_shuffle_id = models.UUIDField(max_length=30, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{str(self.concept)} Shuffle'
