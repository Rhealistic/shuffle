from datetime import datetime, timedelta

from django.db import transaction, models
from django.utils import timezone
from django.conf import settings

from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber
from .mailerlite import update_mailerlite, notify_subscriber

def get_next_day_of_week(day_of_week):
    days_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    if isinstance(day_of_week, str):
        day_of_week = day_of_week.lower()

    today = datetime.today()
    days_until_next_day = (days_mapping[day_of_week] - today.weekday() + 7) % 7
    next_day = today + timedelta(days=days_until_next_day)
    return next_day

def create_subscriber(artist, concept):
    with transaction.atomic():
        subscriber = Subscriber.objects.create(concept=concept, artist=artist)

        try:
            notify_subscriber(artist)
            status = status.HTTP_201_CREATED

        except Exception as e:
            status = status.HTTP_400_BAD_REQUEST
    
        return subscriber

def close_opportunity(opportunity: Opportunity, status: Opportunity.Status):
    if status in [Opportunity.Status.ACCEPTED, Opportunity.Status.SKIP, Opportunity.Status.EXPIRED]:
        opportunity.status = status
        opportunity.closed_at = timezone.now()
        opportunity.save()


        if status == Opportunity.Status.ACCEPTED:
            concept: Concept = opportunity.subscriber.concept

            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    acceptance_count=models.F('acceptance_count') + 1,
                    last_performance=models.F('next_performance'),
                    next_performance=get_next_day_of_week(concept.day_of_week or 'friday'),
                    status=Subscriber.Status.NEXT_PERFORMING
                )
        elif status == Opportunity.Status.EXPIRED:
            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    expired_count=models.F('expired_count') + 1,
                    next_performance=None,
                    last_performance=models.F('next_performance'),
                    status=Subscriber.Status.NEXT_CYCLE
                )
        elif status == Opportunity.Status.SKIP:
            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    skip_count=models.F('skip_count') + 1,
                    next_performance=None,
                    last_performance=models.F('next_performance'),
                    status=Subscriber.Status.NEXT_CYCLE
                )
