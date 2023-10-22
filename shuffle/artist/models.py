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
    photo = models.URLField(help_text="Link to online photo")
    instagram = models.URLField(unique=True)
    country = models.CharField(max_length=3, default="KEN")
    
    artist_id = models.UUIDField(max_length=30, default = uuid.uuid4, editable = False)
    mailerlite_subscriber_id = models.CharField(max_length=30, null=True)
    mailerlite_subscriber_group_id = models.CharField(max_length=30, null=True)

    opportunity_status = models.CharField(max_length=15, choices=OPPORTUNITY_STATUSES, null=True)
    invite_status = models.CharField(max_length=15, choices=INVITE_STATUSES, null=True)
    performance_count = models.PositiveSmallIntegerField(default=0)

    next_performance = models.DateTimeField(null=True)
    last_performance = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "artist_profile"