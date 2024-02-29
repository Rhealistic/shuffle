import uuid

from django.db import models


class Event(models.Model):
    class RecurrenceType(models.IntegerChoices):
        DAILY = 0, "Daily"
        WEEKLY = 1, "Weekly"
        MONTHLY = 2, "Monthly"

    class EndType(models.IntegerChoices):
        NEVER = 0, "Never"
        N_OCCURRENCES = 1, "After N Occurrences"
        END_DATE = 2, "End Date"

    class Status(models.IntegerChoices):
        PENDING = 0, 'Pending'
        SUCCESSFUL = 1, 'Successful'
        CANCELLED = 2, 'Cancelled'
        RESCHEDULED = 3, 'Rescheduled'
        FAILED = 4, 'Failed'


    title = models.CharField(max_length=100, null=True, blank=True)
    event_id = models.UUIDField(max_length=30, default = uuid.uuid4, unique=True)
    
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)

    # is_recurring = models.BooleanField(default=False)
    # recurrence_type = models.PositiveSmallIntegerField(choices=RecurrenceType.choices, null=True)
    # frequency = models.PositiveSmallIntegerField(null=True)
    # end_type = models.PositiveSmallIntegerField(choices=EndType.choices, null=True)
    # end_date = models.DateTimeField(null=True)
    
    venue = models.ForeignKey('venue.Venue', models.SET_NULL, related_name='venues', null=True)
    status = models.PositiveSmallIntegerField(choices=  Status.choices, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.title)


