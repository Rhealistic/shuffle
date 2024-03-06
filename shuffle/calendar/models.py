import uuid

from django.db import models


class Event(models.Model):

    class Status(models.IntegerChoices):
        PENDING = 0, 'Pending'
        SUCCESSFUL = 1, 'Successful'
        CANCELLED = 2, 'Cancelled'
        RESCHEDULED = 3, 'Rescheduled'

    event_id = models.UUIDField(max_length=30, default=uuid.uuid4, unique=True)
    
    title = models.CharField(max_length=100, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=Status.choices, null=True)
    
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.title)


