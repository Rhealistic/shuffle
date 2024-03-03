import africastalking

from django.db import transaction
from django.db import models
from django.db.models.functions import Random

from django.utils import timezone
from datetime import timedelta
from shuffle.artist.utils.discovery import close_opportunity

from shuffle.calendar.models import Event
from shuffle.curator.models import Concept

from ..artist.models import Opportunity, Subscriber
from .models import Shuffle

import logging
logger = logging.getLogger(__name__)

days_ago = lambda d: (timezone.now() - timedelta(days=d))

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

def prepare_invite(shuffle: Shuffle, pick: Subscriber):
    logger.debug(f"prepare_invite({shuffle}, {pick})")

    opportunities = Opportunity.objects\
        .filter(subscriber=pick)\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .order_by('-created_at')
    
    if opportunities.exists():
        opportunity = opportunities.first()

        logger.debug(f"awaiting acceptance for opportunity ({opportunity})")

        opportunity.status = Opportunity.Status.AWAITING_ACCEPTANCE
        opportunity.sent_at = timezone.now()
        opportunity.shuffle_id = shuffle.shuffle_id
        opportunity.save()

        logger.debug(f"opportunity sent for ({opportunity})")

        shuffle.pick = pick
        shuffle.status = Shuffle.Status.INVITE_SENT
        shuffle.save()

        return opportunity
    else:
        logger.debug(f"Opportunity not found for artist")


def do_shuffle(concept: Concept):
    logger.debug(f"do_shuffle(`{concept}`)")

    in_progress = Shuffle.objects\
        .filter(concept=concept)\
        .filter(closed_at__isnull=True)\
        .exists()
    
    if in_progress:
        logger.error(f"Shuffle: shuffle on concept '{concept}' is already in progress")
        return

    with transaction.atomic():
        shuffle = Shuffle.objects.create(
            concept=concept, 
            start_date=timezone.now())
        
        logger.debug(f"Shuffle: created a new shuffle '{shuffle.shuffle_id}'")
        
        concept.shuffle_count += 1
        concept.save()
        
        r = 0
        while r < 5:
            pick: Subscriber = pick_performer(concept)

            if pick:
                logger.debug(f"Shuffle: Retry - {r + 1}: `{pick}` has been picked for concept `{concept}` shuffle")
                pick.selection_count += 1
                pick.save()
                
                logger.debug(f"Shuffle: `{shuffle}` as moved to status IN_PROGRESS")
                shuffle.status = Shuffle.Status.IN_PROGRESS
                shuffle.save()

                logger.debug(f"Shuffle: Sending a performance invite to the `{pick}`")
                return prepare_invite(shuffle, pick)
            
            logger.debug(f"Shuffle: Retry - {r}: The pick was empty, retrying")
            r += 1

        shuffle.status = Shuffle.Status.FAILED
        shuffle.closed_at = timezone.now()
        shuffle.save()


def do_reshuffle(current: Opportunity, opportunity_status):
    logger.debug(f"do_reshuffle({current}, {opportunity_status})")

    with transaction.atomic():
        if close_opportunity(current, opportunity_status):
            shuffle = Shuffle.objects\
                .filter(closed_at__isnull=True)\
                .get(shuffle_id=current.shuffle_id)
            
            shuffle.status = Shuffle.Status.RESHUFFLE
            shuffle.retries += 1
            shuffle.save()

            current.status = opportunity_status
            current.closed_at = timezone.now()
            current.save()

            shuffle.concept.reshuffle_count += 1
            shuffle.concept.save()
        
            r = 0
            while r < 5:
                pick: Subscriber = pick_performer(shuffle.concept)

                if pick:
                    logger.debug(f"Reshuffle: retry - {r + 1}: {pick} has been picked for concept {shuffle.concept} shuffle")

                    pick.selection_count += 1
                    pick.save()

                    return prepare_invite(shuffle, pick)
                
                logger.debug(f"Shuffle: Retry - {r}: The pick was empty, retrying")
                r += 1

            logger.error(f"Reshuffle: Shuffle {shuffle.concept} failed. Did not find an artist in 5 retries")

            shuffle.status = Shuffle.Status.FAILED
            shuffle.closed_at = timezone.now()
            shuffle.save()


def pick_performer(concept: Concept):
    logger.debug(f"pick_performer({concept})")

    subscribers = Subscriber.objects\
        .filter(artist__is_active=True)\
        .filter(is_subscribed=True)\
        .filter(concept=concept)\
        .filter(opportunity__status=Opportunity.Status.PENDING)\
        .filter(opportunity__closed_at__isnull=True)

    with transaction.atomic():
        potentials = subscribers\
            .filter(status=Subscriber.Status.POTENTIAL)
        if potentials.count() > 0:
            logger.debug(f"{potentials.count()} 'POTENTIAL' status subscribers found")

            return potentials\
                .order_by(Random())\
                .first()

        next_cycle = subscribers\
            .filter(status=Subscriber.Status.NEXT_CYCLE)
        if next_cycle.count() > 0:
            logger.debug(f"{next_cycle.count()} 'NEXT_CYCLE' status subscribers found found")

            return next_cycle\
                .order_by(Random())\
                .first()

        performed  = subscribers\
            .filter(status=Subscriber.Status.PERFORMED)

        performed_atmost_once = performed\
            .filter(performance_count__lte=1)

        if performed_atmost_once.count() > 0:
            logger.debug(f"{performed_atmost_once.count()} 'PERFORMED - ATLEAST ONCE' subscribers found found")
            return performed_atmost_once\
                .order_by(Random())\
                .first()
        else:
            logger.debug(f"{performed.count()} 'PERFORMED - MORE THAN ONCE' status subscribers found found")
            return performed\
                .order_by(Random())\
                .first()


def accept_invite(shuffle, opportunity):
    logger.debug(f"accept_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.ACCEPTED):
        shuffle.status = Shuffle.Status.COMPLETE
        shuffle.closed_at = timezone.now()
        shuffle.save()
