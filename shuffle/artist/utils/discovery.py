from django.db import models
from django.utils import timezone

from shuffle.calendar.models import Event
from shuffle.calendar.utils import days_ago
from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber

import logging
logger = logging.getLogger(__name__)


def discover_opportunities(concept: Concept):
    logger.debug(f"discover_opportunities({concept})")

    subscribers = concept\
        .concept_subscriptions\
        .filter(artist__is_active=True)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')
    
    new_opportunities = []

    for subscriber in subscribers:
        logger.info(f"checking subscriber engagement for: {subscriber}")

        # Check if subscriber has meets criteria
        #1. Has no pending requests (in the middle of a shuffle)
        #2. Has not performed on this platform/concept in the past 4 weeks
        #3. Has not skipped an opportunity in the past 2 weeks
        #4. Has not expired an opportunity in the past 4 weeks
        #5. Has not cancelled an event in the past 2 weeks

        un_engaged = subscriber\
            .opportunities\
            .exclude(
                models.Q(status=Opportunity.Status.AWAITING_ACCEPTANCE)
                | models.Q(status=Opportunity.Status.ACCEPTED, subscriber__status=Subscriber.Status.PERFORMED, event__status=Event.Status.SUCCESSFUL, subscriber__last_performance__gte=days_ago(4 * 7))
                | models.Q(status=Opportunity.Status.ACCEPTED, event__status__in=[Event.Status.RESCHEDULED, Event.Status.CANCELLED, Event.Status.FAILED], closed_at__gte=days_ago(2 * 7))
                | models.Q(status=Opportunity.Status.EXPIRED, closed_at__gte=days_ago(4 * 7))
                | models.Q(status=Opportunity.Status.SKIP, closed_at__gte=days_ago(2 * 7)))
        
        if not un_engaged.exists():
            logger.info(f"potential subscriber has not been engaged recently: {subscriber}")

            new_opportunities.append(
                Opportunity
                    .objects
                    .create(subscriber=subscriber))
            
            logger.info(f"opportunity created for: {subscriber}")
            
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
                    last_performance=models.F('next_performance'),
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
                    last_performance=models.F('next_performance'),
                    status=Subscriber.Status.NEXT_CYCLE
                )
        elif status == Opportunity.Status.SKIP:
            logger.debug(f"status SKIP")

            return Subscriber.objects\
                .filter(id=opportunity.subscriber_id)\
                .update(
                    skip_count=models.F('skip_count') + 1,
                    next_performance=None,
                    last_performance=models.F('next_performance'),
                    status=Subscriber.Status.NEXT_CYCLE
                )
    else:
        logger.error(f"status not allowed here")
