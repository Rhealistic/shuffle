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

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Curator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    curator_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)
    organization = models.ForeignKey('Organization', 
        models.SET_NULL, null=True, related_name='curators', related_query_name='curator')

    last_shuffle = models.DateTimeField(null=True, blank=True)
    next_shuffle = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Concept(models.Model):
    class RecurrenceType(models.IntegerChoices):
        DAILY = 0, "Daily"
        WEEKLY = 1, "Weekly"
        MONTHLY = 2, "Monthly"

    class DayOfWeek(models.IntegerChoices):
        SUNDAY = 0, "Sunday"
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"

    concept_id = models.UUIDField(max_length=30, default = uuid.uuid4)
    curator = models.ForeignKey('Curator', models.SET_NULL, null=True)

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=75, null=True)
    description = models.CharField(max_length=500)

    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.PositiveSmallIntegerField(choices=RecurrenceType.choices, null=True)
    times_per_week = models.PositiveSmallIntegerField(blank=True, null=True)
    times_per_month = models.PositiveSmallIntegerField(blank=True, null=True)
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    shuffle_count = models.PositiveSmallIntegerField(default=0)
    reshuffle_count = models.PositiveSmallIntegerField(default=0)

    is_active = models.BooleanField(default=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title


class Shuffle(models.Model):

    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        IN_PROGRESS = 1, "In Progress"
        INVITE_SENT = 2, "Invite Sent"
        RESHUFFLE = 3, "Reshuffle"
        COMPLETE = 4, "Complete"
        FAILED = 5, "Failed"
    
    shuffle_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)
    concept    = models.ForeignKey('Concept', models.SET_NULL, null=True)

    pick    = models.ForeignKey("artist.Subscriber", models.SET_NULL, null=True)
    status  = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.PENDING)

    retries = models.PositiveSmallIntegerField(default=0)
    start_date  = models.DateTimeField(null=True)
    closed_at   = models.DateTimeField(null=True)

    previous_shuffle_id = models.UUIDField(max_length=30, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{str(self.concept)} Shuffle'
