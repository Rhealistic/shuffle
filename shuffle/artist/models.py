from django.db import models

# Create your models here
class Artist(models.Model):
    name  = models.CharField(max_length=16)
    bio   = models.CharField(max_length=320)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to ='artist-photos/')
    instagram = models.URLField(unique=True)

    opportunity_status = models.CharField(max_length=15, choices=[
        ('WAITING', 'Waiting'),
        ('PERFORMED', 'Performed'),
        ('NEXT_CYCLE', 'Next Cycle')
    ])
    invite_status = models.CharField(max_length=15, choices=[
        ('ACCEPTED', "Accepted"),
        ('REJECTED', "Accepted"),
        ('UNAVAILABLE', "Unavailable"),
    ])
    country = models.CharField(max_length=3, default="KEN")

    performance_count = models.PositiveSmallIntegerField(default=0)
    next_performance = models.DateTimeField(null=True)
    last_performance = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "artist_profile"