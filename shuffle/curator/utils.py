from django.db import transaction
from django.db.models import F
from django.db.models.functions import Random

from django.utils import timezone
from datetime import timedelta
from shuffle.artist.utils.discovery import close_opportunity

from shuffle.calendar.models import Event

from ..artist.models import Opportunity, Subscriber
from .models import Shuffle

from django.db import models
from shuffle.curator.models import Concept

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
        logger.info("checking subscriber engagement for:", subscriber)

        # Check if subscriber has meets criteria
        #1. Has no pending requests (in the middle of a shuffle)
        #2. Has not peformed on this platform/concept in the past 4 weeks
        #3. Has not skipped an opportunity in the past 2 weeks
        #4. Has not expired an opportunity in the past 4 weeks
        #5. Has not cancelled an event in the past 2 weeks

        un_engaged = subscriber\
            .opportunities\
            .exclude(
                (
                    models.Q(status=Opportunity.Status.AWAITING_ACCEPTANCE)
                ) | 
                (
                    models.Q(status=Opportunity.Status.ACCEPTED, subscriber__status=Subscriber.Status.PERFORMED, event__status=Event.Status.SUCCESSFUL, subscriber__last_performance__gte=days_ago(4 * 7)) 
                ) | 
                (
                    models.Q(status=Opportunity.Status.ACCEPTED, event__status__in=[Event.Status.RESCHEDULED, Event.Status.CANCELLED, Event.Status.FAILED], closed_at__gte=days_ago(2 * 7))
                ) | 
                (
                    models.Q(status=Opportunity.Status.EXPIRED, closed_at__gte=days_ago(4 * 7))
                ) | 
                (
                    models.Q(status=Opportunity.Status.SKIP, closed_at__gte=days_ago(2 * 7))
                )
            )
        
        if not un_engaged.exists():
            logger.info("potential subscriber has not been engaged recently:", subscriber)

            new_opportunities.append(
                Opportunity
                    .objects
                    .create(subscriber=subscriber))
            
            logger.info("opportunity created for:", subscriber)
            
    return new_opportunities

def prepare_invite(shuffle: Shuffle, pick: Subscriber):
    logger.debug(f"prepare_invite({shuffle})")

    opportunity = Opportunity.objects\
        .filter(subscriber=pick)\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .order_by('-created_at')\
        .first()
    
    if opportunity:
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


def do_shuffle(concept: Concept):
    logger.debug(f"do_shuffle({concept})")

    with transaction.atomic():
        in_progress = Shuffle.objects\
            .filter(concept=concept)\
            .filter(closed_at__isnull=True)\
            .exists()
        
        if in_progress:
            logger.error(f"shuffle on concept '{concept}' is in progress")
            return
        
        try:
            previous_shuffle = Shuffle.objects\
                .filter(concept=concept)\
                .filter(closed_at__isnull=False)\
                .latest('created_at')
        except Shuffle.DoesNotExist as e:
            logging.exception(e)
            previous_shuffle = None
        
        shuffle = Shuffle.objects.create(
            concept=concept, 
            start_date=timezone.now(),
            status=Shuffle.Status.IN_PROGRESS,
            previous_shuffle_id=previous_shuffle.shuffle_id if previous_shuffle else None)
        
        logger.debug(f"created a new shuffle '{shuffle.shuffle_id}' previous shuffle {shuffle.shuffle_id}")
        
        concept.shuffle_count += 1
        concept.save()
        
        r = 0
        while r < 5:
            pick: Subscriber = pick_performer(concept)
            pick.selection_count += 1
            pick.save()

            logger.debug(f"retry - {r}: {pick} has been picked for concept {concept} shuffle")

            if pick:
                return prepare_invite(shuffle, pick)

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

            shuffle.concept.reshuffle_count += 1
            shuffle.concept.save()
        
            r = 0
            while r < 5:
                pick: Subscriber = pick_performer(shuffle.concept)
                pick.selection_count += 1
                pick.save()
                
                logger.debug(f"retry - {r}: {pick} has been picked for concept {shuffle.concept} shuffle")

                if pick:
                    return prepare_invite(shuffle, pick)

                r += 1

            logger.error(f"Shuffle {shuffle.concept} failed. Did not find an artist in 5 retries")

            shuffle.status = Shuffle.Status.FAILED
            shuffle.closed_at = timezone.now()
            shuffle.save()


def pick_performer(concept: Concept):
    logger.debug(f"pick_performer({concept})")

    with transaction.atomic():
        subscribers = Subscriber.objects\
            .filter(artist__is_active=True)\
            .filter(is_subscribed=True)\
            .filter(concept=concept)\
            .filter(opportunity__closed_at__isnull=True)
        
        potentials = subscribers.filter(status=Subscriber.Status.POTENTIAL)
        next_cycle = subscribers.filter(status=Subscriber.Status.NEXT_CYCLE)
        performed  = subscribers.filter(status=Subscriber.Status.PERFORMED)

        pick: Subscriber = None

        if potentials.count() > 0:
            logger.debug(f"{potentials.count()} 'POTENTIAL' status subscribers found")
            pick = potentials\
                .order_by(Random())\
                .first()
        elif next_cycle.count() > 0:
            logger.debug(f"{next_cycle.count()} 'NEXT_CYCLE' status subscribers found found")

            pick = next_cycle\
                .order_by(Random())\
                .first()
        elif performed.count() > 0:
            performed_atmost_once = performed.filter(subscription__performance_count_lte=1)

            if performed_atmost_once.count > 0:
                logger.debug(f"{performed.count()} 'PERFORMED - ATLEAST ONCE' subscribers found found")
                pick = performed_atmost_once.order_by(Random()).first()
            else:
                logger.debug(f"{performed.count()} 'PERFORMED - MORE THAN ONCE' status subscribers found found")
                pick = performed.order_by(Random()).first()
        
        logger.debug(f"{pick} picked!")

        return pick


def accept_invite(shuffle, opportunity):
    logger.debug(f"accept_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.ACCEPTED):
        shuffle.status = Shuffle.Status.COMPLETE
        shuffle.closed_at = timezone.now()
        shuffle.save()
