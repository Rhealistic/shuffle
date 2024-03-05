import datetime

from django.utils import timezone
from shuffle.curator.models import Concept

import logging
logger = logging.getLogger(__name__)

def hours_ago(h): return timezone.now() - datetime.timedelta(hours=h)
def days_ago(d):  return timezone.now() - datetime.timedelta(days=d)

def get_concept_event_dates(concept: Concept, limit=1):
    if concept.is_recurring and concept.recurrence_type == Concept.RecurrenceType.WEEKLY:
        if concept.start_date is None:
            start_date = get_next_date_day_of_week(concept.day_of_week)
        else:
            start_date = concept.start_date

        return get_weekly_event_times(
            start_date, 
            concept.start_time, 
            concept.end_time,
            limit
        )


def get_weekly_event_times(start_date=None, start_time=None, end_time=None, no_of_weeks=1):
    logger.debug(f"get_next_day_of_week({start_date}, {start_time}, {end_time}, {no_of_weeks})")

    ranges = []

    if start_date:
        current_date = start_date
    else:
        current_date = timezone.now().date()

    if start_time:
        start_time = start_time
    else:
        start_time = timezone.now().time()
        
    if not end_time:
        end_time = (timezone.now() + datetime.timedelta(hours=1)).time()

    for _ in range(no_of_weeks):
        start_datetime = datetime.datetime.combine(current_date, start_time)
        end_datetime = datetime.datetime.combine(current_date, end_time)
        ranges.append((start_datetime, end_datetime))

        current_date += datetime.timedelta(days=7)

    logger.debug(f"ranges={ranges}")
    
    return ranges


def get_next_date_day_of_week(day_of_week):
    logger.debug(f"get_next_date_day_of_week({day_of_week})")

    today = timezone.now()
    current_weekday = today.weekday()
    days_difference = day_of_week - current_weekday

    if days_difference < 0:
        days_difference += 7

    target_datetime = today + datetime.timedelta(days=days_difference)
    target_datetime = target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    return target_datetime