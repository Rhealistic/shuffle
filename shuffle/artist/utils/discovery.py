from django.db import models
from django.utils import timezone

from shuffle.calendar.models import Event
from shuffle.calendar.utils import days_ago
from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber

import logging
logger = logging.getLogger(__name__)


def close_lapsed_events(concept: Concept):
    logger.debug(f"close_lapsed_events({concept})")

    events = Event.objects\
        .filter(end__lte=timezone.now())\
        .filter(concept_opportunity__subscriber__concept=concept)\
        .filter(closed_at__isnull=True)
    
    for event in events:
        close_event(event, Event.Status.SUCCESSFUL)


def create_opportunity(subscriber: Subscriber):
    # Check if subscriber has meets criteria
    #1. Has no pending requests (in the middle of a shuffle)
    current_pending_requests = models.Q(status__in=[
        Opportunity.Status.PENDING,
        Opportunity.Status.AWAITING_ACCEPTANCE,
    ])
    #2. Has not performed on this platform/concept in the past 4 weeks
    recent_performance = models.Q(
        status=Opportunity.Status.ACCEPTED, 
        subscriber__status=Subscriber.Status.PERFORMED, 
        event__status=Event.Status.SUCCESSFUL, 
        subscriber__last_performance__gte=days_ago(28)
    )
    #3. Has not skipped an opportunity in the past 2 weeks
    recent_skips = models.Q(status=Opportunity.Status.SKIP, closed_at__gte=days_ago(14))
    #4. Has not expired an opportunity in the past 4 weeks
    recent_expirations = models.Q(status=Opportunity.Status.EXPIRED, closed_at__gte=days_ago(28))
    #5. Has not cancelled an event in the past 2 weeks
    recent_cancellations = models.Q(
        status=Opportunity.Status.ACCEPTED, 
        event__status__in=[Event.Status.RESCHEDULED, Event.Status.CANCELLED], 
        closed_at__gte=days_ago(14))

    un_engaged: models.QuerySet[Opportunity] = subscriber\
        .opportunities\
        .exclude(
            current_pending_requests 
            | recent_performance 
            | recent_skips 
            | recent_expirations 
            | recent_cancellations
        )
    
    if not un_engaged.exists():
        logger.info(f"potential subscriber has not been engaged recently: {subscriber}")

        logger.info(f"opportunity created for: {subscriber}")
        return Opportunity\
                .objects\
                .create(subscriber=subscriber)
        

def discover_opportunities(concept: Concept):
    logger.debug(f"discover_opportunities({concept})")

    close_lapsed_events(concept)

    subscribers: models.QuerySet[Subscriber] = concept\
        .concept_subscriptions\
        .filter(artist__is_active=True)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')
    
    new_opportunities = []

    for subscriber in subscribers:
        logger.info(f"checking subscriber engagement for: {subscriber}")
        
        opportunity = create_opportunity(subscriber)
        logger.debug(f"Opportunity for {subscriber.artist}")

        new_opportunities.append(opportunity)
            
    return new_opportunities


def close_opportunity(opportunity: Opportunity, status: Opportunity.Status):
    logger.debug(f"close_opportunity({opportunity}, {status})")

    if status in [Opportunity.Status.ACCEPTED, Opportunity.Status.SKIP, Opportunity.Status.EXPIRED]:
        opportunity.status = status
        opportunity.closed_at = timezone.now()
        opportunity.save(update_fields=['status', 'closed_at'])
        opportunity.refresh_from_db()

        if status == Opportunity.Status.ACCEPTED:
            logger.debug(f"status ACCEPTED")

            concept: Concept = opportunity.subscriber.concept
            
            (start_time, end_time) = concept.get_next_event_timing()
            opportunity.event = Event.objects.create(
                title=f"{opportunity.subscriber.artist.name} performs at {concept.title}",
                start=start_time,
                end=end_time
            )
            opportunity.save(update_fields=['event'])
            opportunity.refresh_from_db()

            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    acceptance_count=models.F('acceptance_count') + 1,
                    next_performance=start_time,
                    status=Subscriber.Status.NEXT_PERFORMING
                )
        elif status == Opportunity.Status.EXPIRED:
            logger.debug(f"status EXPIRED")

            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    expired_count=models.F('expired_count') + 1,
                    next_performance=None,
                    status=Subscriber.Status.NEXT_CYCLE
                )
        elif status == Opportunity.Status.SKIP:
            logger.debug(f"status SKIP")

            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    skip_count=models.F('skip_count') + 1,
                    next_performance=None,
                    status=Subscriber.Status.NEXT_CYCLE
                )
    else:
        logger.error(f"status not allowed here")


def close_event(event: Event, status: Event.Status):
    logger.debug(f"close_event({event}, {status})")

    subscriber = Subscriber.objects\
        .filter(opportunity__event=event)\
        .first()
    
    if subscriber:
        logger.debug(f"event subscriber = {subscriber}")

        if status == Event.Status.SUCCESSFUL:
            subscriber.status = Subscriber.Status.PERFORMED
        elif status in [Event.Status.RESCHEDULED, Event.Status.CANCELLED]:
            subscriber.status = Subscriber.Status.NEXT_UP

        subscriber.last_performance = subscriber.next_performance
        subscriber.next_performance = None
        subscriber.save(update_fields=['status', 'last_performance', 'next_performance'])

        event.status = status
        event.closed_at = timezone.now()
        event.save(update_fields=['status', 'closed_at'])
        
        return True

