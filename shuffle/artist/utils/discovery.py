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

        if status == Opportunity.Status.ACCEPTED:
            logger.debug(f"status ACCEPTED")

            event_date = get_next_date_day_of_week(concept.day_of_week or 'friday')
            concept: Concept = opportunity.subscriber.concept

            event_dates = get_concept_event_dates(concept)
            opportunity.event = Event.objects.create(
                title=f"{opportunity.subscriber.artist.name} performs at {concept.title}",
                # start=
                # end=
            )

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
