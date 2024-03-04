from django.db import models
from django.utils import timezone
from shuffle.calendar.models import Event
from shuffle.calendar.utils import get_concept_event_dates, get_next_date_day_of_week

from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber

import logging
logger = logging.getLogger(__name__)

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
            
            event_dates = get_concept_event_dates(concept)
            for event_date in event_dates:
                opportunity.event = Event.objects.create(
                    title=f"{opportunity.subscriber.artist.name} performs at {concept.title}",
                    start=event_date[0],
                    end=event_date[1]
                )
                opportunity.save(update_fields=['event'])
                opportunity.refresh_from_db()

                return Subscriber.objects\
                    .filter(id=opportunity.subscriber_id)\
                    .update(
                        acceptance_count=models.F('acceptance_count') + 1,
                        last_performance=models.F('next_performance'),
                        next_performance=event_date,
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
