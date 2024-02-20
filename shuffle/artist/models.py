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

    selection_count = models.PositiveSmallIntegerField(default=0)
    acceptance_count = models.PositiveSmallIntegerField(default=0)
    expired_count = models.PositiveSmallIntegerField(default=0)
    skip_count = models.PositiveSmallIntegerField(default=0)
    performance_count = models.PositiveSmallIntegerField(default=0)

    next_performance = models.DateTimeField(null=True, blank=True)
    last_performance = models.DateTimeField(null=True, blank=True)
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
            photo=self.photo,
            instagram=self.instagram,
            country=self.country,
            artist_id=self.artist_id,
            mailerlite_subscriber_id=self.mailerlite_subscriber_id,
            mailerlite_subscriber_group_id=self.mailerlite_subscriber_group_id,
            performance_count=self.performance_count,
            next_performance=self.next_performance,
            last_performance=self.last_performance,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class Opportunity(models.Model):
    concept = models.ForeignKey('curator.Concept', models.SET_NULL, null=True)
    artist  = models.ForeignKey('Artist', models.SET_NULL, related_name='artists', null=True)

    POTENTIAL = 0
    WAITING_APPROVAL = 1
    NEXT_PERFORMING = 2
    PERFORMED = 3
    NEXT_CYCLE = 4
    SKIP = 5
    EXPIRED = 6
    OPPORTUNITY_STATUSES = [
        (POTENTIAL, 'Potential'),
        (WAITING_APPROVAL, 'Waiting Approval'),
        (NEXT_PERFORMING, 'Next Performing'),
        (PERFORMED, 'Performed'),
        (SKIP, 'Skip'),
        (EXPIRED, 'Expired')
    ]
    status = models.PositiveSmallIntegerField(
        choices=OPPORTUNITY_STATUSES, default=WAITING_APPROVAL, null=True
    )

    skipped_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{self.concept}: {self.artist}'
