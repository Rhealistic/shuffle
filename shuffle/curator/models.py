import uuid
import json

from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True)
    bio = models.TextField(max_length=1000, null=True)

    organization_id = models.UUIDField(max_length=30, default = uuid.uuid4, db_index=True, unique=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)
    logo = models.URLField(max_length=500, null=True, blank=True)
    
    website = models.URLField(max_length=150, null=True, blank=True)

    is_active = models.BooleanField(default=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Curator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    curator_id = models.UUIDField(max_length=30, default = uuid.uuid4, db_index=True, unique=True)
    organization = models.ForeignKey('Organization', 
        models.SET_NULL, null=True, related_name='curators', related_query_name='curator')

    last_shuffle = models.DateTimeField(null=True, blank=True)
    next_shuffle = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Concept(models.Model):
    class EndType(models.IntegerChoices):
        NEVER = 0, "Never"
        N_OCCURRENCES = 1, "After N Occurrences"
        END_DATE = 2, "End Date"

    class RecurrenceType(models.IntegerChoices):
        DAILY = 0, "Daily"
        WEEKLY = 1, "Weekly"
        BIWEEKLY = 2, "Bieekly"
        MONTHLY = 3, "Monthly"
        QUARTERLY = 4, "Quarterly"

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    concept_id = models.UUIDField(max_length=30, default = uuid.uuid4, db_index=True, unique=True)
    curator = models.ForeignKey('Curator', models.SET_NULL, null=True)

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=75, unique=True)
    description = models.TextField(max_length=500)

    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.PositiveSmallIntegerField(choices=RecurrenceType.choices, null=True)
    times_per_week = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    times_per_month = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices, null=True, blank=True)
    end_type = models.PositiveSmallIntegerField(choices=EndType.choices, default=EndType.NEVER, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    shuffle_count = models.PositiveSmallIntegerField(default=0)
    reshuffle_count = models.PositiveSmallIntegerField(default=0)

    is_active = models.BooleanField(default=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title
    
    def get_next_event_timing(self):
        from shuffle.calendar.utils import get_concept_event_dates
        return get_concept_event_dates(self)[0]


class Shuffle(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        IN_PROGRESS = 1, "In Progress"
        INVITE_SENT = 2, "Invite Sent"
        RESHUFFLE = 3, "Reshuffle"
        COMPLETE = 4, "Complete"
        FAILED = 5, "Failed"
    
    shuffle_id = models.UUIDField(max_length=30, default=uuid.uuid4, db_index=True, unique=True)
    concept = models.ForeignKey('Concept', models.SET_NULL, null=True)

    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.PENDING)
    pick = models.ForeignKey("artist.Subscriber", models.SET_NULL, null=True, blank=True)
    retries = models.PositiveSmallIntegerField(default=0)
    
    start_time = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{str(self.concept)} Shuffle'


class Config(models.Model):
    class ConfigType(models.IntegerChoices):
        JSON_CONFIG = 0, "JSON Config"
        ACTIVEPIECES_WEBHOOK = 1, "Activepieces Webhook"
        SMS_TEMPLATE = 2, "SMS Template"

    config_id = models.UUIDField(max_length=30, default = uuid.uuid4, db_index=True, unique=True)

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    type = models.PositiveSmallIntegerField(choices=ConfigType.choices, default=ConfigType.JSON_CONFIG)

    class Meta:
        db_table = "system_config"

    def get_json(self):
        if self.type == self.ConfigType.JSON_CONFIG:
            return json.loads(self.value)