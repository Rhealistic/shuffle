import uuid 
from django.db import models


class Artist(models.Model):
    name  = models.CharField(max_length=16)
    bio   = models.TextField(max_length=500)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    country = models.CharField(max_length=3, default="KEN")
    
    photo = models.URLField(help_text="Link to online photo", blank=True, null=True)
    mixcloud = models.URLField(help_text="Link to mixcloud", blank=True, null=True)
    soundcloud = models.URLField(help_text="Link to soundcloud", blank=True, null=True)
    epk = models.URLField(help_text="Link to EPK + Tech rider", blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    artist_id = models.UUIDField(max_length=30, default=uuid.uuid4, db_index=True, unique=True)
    mailerlite_subscriber_id = models.CharField(max_length=30, null=True, blank=True)
    mailerlite_subscriber_group_id = models.CharField(max_length=30, null=True, blank=True)

    is_active = models.BooleanField(null=True, default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "artist_profile"


class Subscriber(models.Model):
    class Status(models.IntegerChoices):
        # has been identified as a potential performer
        POTENTIAL = 0, "Potential" 
        # event outcome was unsuccessful; second chance
        NEXT_UP = 2, "Next Up"
        # shuffle was successful; has been chosen to perform in the next event of the concept
        NEXT_PERFORMING = 3, "Next Performing" 
        # shuffle was successful; event was successful, artist performed
        PERFORMED  = 4, "Performed" 
        # shuffle was unsuccessful;
        NEXT_CYCLE = 5, "Next Cycle"

    subscriber_id = models.UUIDField(max_length=30, default=uuid.uuid4, db_index=True, unique=True)

    concept = models.ForeignKey('curator.Concept', models.CASCADE, 
        related_name='concept_subscriptions', related_query_name='concept_subscription')
    artist  = models.ForeignKey('Artist', models.CASCADE, 
        related_name='subscriptions', related_query_name='subscription')

    status = models.PositiveSmallIntegerField(
        choices=Status.choices, null=True,default=Status.POTENTIAL)

    sms_count = models.PositiveSmallIntegerField(default=0)
    selection_count = models.PositiveSmallIntegerField(default=0)
    acceptance_count = models.PositiveSmallIntegerField(default=0)
    expired_count = models.PositiveSmallIntegerField(default=0)
    skip_count = models.PositiveSmallIntegerField(default=0)
    performance_count = models.PositiveSmallIntegerField(default=0)

    next_performance = models.DateTimeField(null=True, blank=True)
    last_performance = models.DateTimeField(null=True, blank=True)

    is_subscribed = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return f'{self.concept}: {self.artist}'
    

class Opportunity(models.Model):
    # pending > awaiting acceptance > (accepted | skip | expired)
    class Status(models.IntegerChoices):
        PENDING = 0, 'Pending'
        AWAITING_ACCEPTANCE = 1, 'Awaiting Acceptance'
        ACCEPTED = 2, 'Accepted'
        SKIP = 3, 'Skipped'
        EXPIRED = 4, 'Expired'

    class RejectReason(models.IntegerChoices):
        NONE = 0, '------'
        UNAVAILABLE = 1, 'Unavailable'
        RESCHEDULE = 2, 'Reschedule'
        PASS = 3, 'Pass'

    shuffle_id = models.UUIDField(null=True, blank=True, db_index=True)
    opportunity_id = models.UUIDField(default= uuid.uuid4, db_index=True, unique=True)
    
    subscriber = models.ForeignKey('Subscriber', models.SET_NULL, null=True, 
        related_name='opportunities', related_query_name='opportunity')
    event = models.ForeignKey('calendar.Event', models.SET_NULL, null=True, blank=True, 
        related_name='concept_opportunities', related_query_name='concept_opportunity')
    
    status = models.PositiveSmallIntegerField(choices=Status.choices, null=True, default=Status.PENDING)

    notes_to_curator = models.TextField(max_length=250, null=True)
    reject_reason = models.PositiveSmallIntegerField(choices=RejectReason.choices, null=True)

    sent_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return str(self.subscriber)
