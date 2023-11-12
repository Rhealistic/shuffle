import uuid 
from django.db import models

OPPORTUNITY_STATUSES = [
    ('WAITING', 'Waiting'),
    ('PERFORMED', 'Performed'),
    ('NEXT_CYCLE', 'Next Cycle')
]
INVITE_STATUSES = [
    ('ACCEPTED', "Accepted"),
    ('REJECTED', "Accepted"),
    ('UNAVAILABLE', "Unavailable"),
]

class Artist(models.Model):
    name  = models.CharField(max_length=16)
    bio   = models.CharField(max_length=320)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    photo = models.URLField(help_text="Link to online photo", blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=3, default="KEN")
    
    artist_id = models.UUIDField(max_length=30, default = uuid.uuid4, editable = False)
    mailerlite_subscriber_id = models.CharField(max_length=30, null=True, blank=True)
    mailerlite_subscriber_group_id = models.CharField(max_length=30, null=True, blank=True)

    opportunity_status = models.CharField(max_length=15, choices=OPPORTUNITY_STATUSES, default="WAITING")
    invite_status = models.CharField(max_length=15, choices=INVITE_STATUSES, null=True, blank=True)
    performance_count = models.PositiveSmallIntegerField(default=0)

    next_performance = models.DateTimeField(null=True, blank=True)
    last_performance = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

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
            opportunity_status=self.opportunity_status,
            invite_status=self.invite_status,
            performance_count=self.performance_count,
            next_performance=self.next_performance,
            last_performance=self.last_performance,
            created_at=self.created_at,
            updated_at=self.updated_at
        )