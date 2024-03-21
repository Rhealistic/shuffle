from datetime import timedelta
from time import sleep
from django.db import transaction
from django.db.models.functions import Random
from django.db.models.query import QuerySet

from django.utils import timezone
from shuffle.artist.utils.discovery import close_opportunity
from shuffle.curator.models import Concept

from shuffle.artist.models import Opportunity, Subscriber
from .invites import prepare_invite
from ..models import Shuffle

import logging
logger = logging.getLogger(__name__)


def prepare_shuffles():
    shuffles = []

    active_concepts = Concept.objects\
        .filter(curator__organization__is_active=True)\
        .filter(curator__is_active=True)\
        .filter(is_active=True)
    for concept in active_concepts:
        shuffles.append(
            Shuffle.objects
                .create(
                    concept=concept,
                    status=Shuffle.Status.PENDING,
                    start_time=timezone.now()
                )
        )
    
    return shuffles


def do_shuffle(shuffle: Shuffle):
    logger.debug(f"do_shuffle(`{shuffle.shuffle_id}{shuffle.concept}`)")

    concept = shuffle.concept
    assert shuffle.status == Shuffle.Status.PENDING and shuffle.closed_at is None, "Shuffle has already been processed"

    with transaction.atomic():
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
            sleep(5)

        shuffle.status = Shuffle.Status.FAILED
        shuffle.closed_at = timezone.now()
        shuffle.save()


def do_reshuffle(previous: Opportunity, opportunity_status):
    logger.debug(f"do_reshuffle({previous}, {opportunity_status})")

    with transaction.atomic():
        if close_opportunity(previous, opportunity_status):
            shuffle = Shuffle.objects\
                .filter(closed_at__isnull=True)\
                .get(shuffle_id=previous.shuffle_id)
            
            shuffle.status = Shuffle.Status.RESHUFFLE
            shuffle.retries += 1
            shuffle.save()

            previous.status = opportunity_status
            previous.closed_at = timezone.now()
            previous.save()

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


def pick_performer(concept: Concept) -> Subscriber:
    logger.debug(f"pick_performer({concept})")

    potential_picks: QuerySet[Subscriber] = Subscriber.objects\
        .filter(artist__is_active=True)\
        .filter(is_subscribed=True)\
        .filter(concept=concept)\
        .filter(opportunity__status=Opportunity.Status.PENDING)\
        .filter(opportunity__closed_at__isnull=True)

    def get_random_subscriber(subscribers) -> Subscriber:
        return subscribers.order_by(Random()).first()

    with transaction.atomic():
        for status in [
            Subscriber.Status.POTENTIAL, # are new artists that have just subscribed
            Subscriber.Status.NEXT_UP, # the artist selected for the next performance
            Subscriber.Status.NEXT_CYCLE, # artist
            Subscriber.Status.PERFORMED # 
        ]:
            subscribers: QuerySet[Subscriber] = potential_picks.filter(status=status)

            if status == Subscriber.Status.PERFORMED:
                if subscribers.filter(performance_count__lte=1).count() > 0:
                    logger.debug(f"{subscribers.filter(performance_count__lte=1).count()} '{status} - ATLEAST ONCE' status subscribers found")
                    return get_random_subscriber(subscribers.filter(performance_count__lte=1))
                elif subscribers.count():
                    return get_random_subscriber(subscribers)
            else:
                if subscribers.count():
                    logger.debug(f"{subscribers.count()} '{status}' status subscribers found")
                    return get_random_subscriber(subscribers)
              

         