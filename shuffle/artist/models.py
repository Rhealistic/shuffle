import uuid 
from django.db import models


class Artist(models.Model):
    name  = models.CharField(max_length=16)
    bio   = models.CharField(max_length=320)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    country = models.CharField(max_length=3, default="KEN")
    
    photo = models.URLField(help_text="Link to online photo", blank=True, null=True)
    mixcloud = models.URLField(help_text="Link to mixcloud", blank=True, null=True)
    soundcloud = models.URLField(help_text="Link to soundcloud", blank=True, null=True)
    epk = models.URLField(help_text="Link to EPK + Tech rider", blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    artist_id = models.UUIDField(max_length=30, default = uuid.uuid4)
    mailerlite_subscriber_id = models.CharField(max_length=30, null=True, blank=True)
    mailerlite_subscriber_group_id = models.CharField(max_length=30, null=True, blank=True)

    is_active = models.BooleanField(null=True, default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "artist_profile"

    def dict(self):
        return dict(
            name=self.name,
            bio=self.bio,
            email=self.email,
            phone=self.phone,
            epk=self.epk,
            photo=self.photo,
            mixcloud=self.mixcloud,
            soundcloud=self.soundcloud,
            instagram=self.instagram,
            country=self.country,
            artist_id=self.artist_id,
            mailerlite_subscriber_id=self.mailerlite_subscriber_id,
            mailerlite_subscriber_group_id=self.mailerlite_subscriber_group_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class Subscriber(models.Model):
    subscriber_id = models.UUIDField(max_length=30, default = uuid.uuid4)

    concept = models.ForeignKey('curator.Concept', models.CASCADE, related_name='concepts')
    artist  = models.ForeignKey('Artist', models.CASCADE, related_name='subscriptions')

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
    
    
    def dict(self):
        return dict(
            subscriber_id=self.subscriber_id,
            concept_id=self.concept.concept_id,
            artist_id=self.artist.artist_id,
            selection_count=self.selection_count,
            acceptance_count=self.acceptance_count,
            expired_count=self.expired_count,
            skip_count=self.skip_count,
            performance_count=self.performance_count,
            next_performance=self.next_performance,
            last_performance=self.last_performance,
            is_subscribed=self.is_subscribed,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class Opportunity(models.Model):
    class OpportunityStatus(models.IntegerChoices):
        # has been identified as a potential performer
        POTENTIAL = 0, "Potential" 
        # has been chosen to perform in the next event of the concept
        NEXT_PERFORMING = 1, "Next Performing" 
        # outcome was successful; artist performed
        PERFORMED  = 2, "Performed" 
        # outcome was unsuccessful; opportunity expired or artist skipped.
        NEXT_CYCLE = 3, "Next Cycle"

    class InviteStatus(models.IntegerChoices):
        PENDING = 0, 'Pending'
        SENT = 1, 'Sent'
        WAITING_ACCEPTANCE = 2, 'Awaiting Acceptance'
        ACCEPTED = 3, 'Accepted'
        SKIP = 4, 'Skip'
        EXPIRED = 5, 'Expired'

    opportunity_id = models.UUIDField(max_length=30, default = uuid.uuid4)
    subscriber = models.ForeignKey('Subscriber', models.SET_NULL, null=True)

    status = models.PositiveSmallIntegerField(
        choices=OpportunityStatus.choices, null=True,
        default=OpportunityStatus.POTENTIAL
    )
    invite_status = models.PositiveSmallIntegerField(
        choices=InviteStatus.choices, null=True, 
        default=InviteStatus.PENDING
    )

    skipped_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return str(self.subscriber)

    def dict(self):
        return dict(
            opportunity_id=self.opportunity_id,
            subscriber_id=self.subscriber.subscriber_id,
            status=self.status,
            invite_status=self.invite_status,
            skipped_at=self.skipped_at,
            accepted_at=self.accepted_at,
            expired_at=self.expired_at,
            created_at=self.created_at,
            updated_at=self.updated_at
        )