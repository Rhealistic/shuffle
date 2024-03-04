from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber

import logging
logger = logging.getLogger(__name__)

def get_next_day_of_week(day_of_week):
    logger.debug(f"get_next_day_of_week({day_of_week})")

    days_mapping = {
        'sunday': 0,
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
    }

    day = day_of_week
    if isinstance(day_of_week, str):
        day = days_mapping[day_of_week.lower()]

    today = datetime.today()
    days_until_next_day = (day - today.weekday() + 7) % 7
    next_day = today + timedelta(days=days_until_next_day)

    logger.debug(f"next_day({next_day})")

    return next_day

def close_opportunity(opportunity: Opportunity, status: Opportunity.Status):
    logger.debug(f"close_opportunity({opportunity}, {status})")

    if status in [Opportunity.Status.ACCEPTED, Opportunity.Status.SKIP, Opportunity.Status.EXPIRED]:
        opportunity.status = status
        opportunity.closed_at = timezone.now()
        opportunity.save(update_fields=['status', 'closed_at'])

        if status == Opportunity.Status.ACCEPTED:
            logger.debug(f"status ACCEPTED")

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
