from django.db import transaction
from django.db.models.functions import Random

from django.utils import timezone
from shuffle.artist.utils.discovery import close_opportunity
from shuffle.curator.models import Concept

from shuffle.artist.models import Opportunity, Subscriber
from .invites import prepare_invite
from ..models import Shuffle

import logging
logger = logging.getLogger(__name__)

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
            logger.debug(f"{next_cycle.count()} 'NEXT_CYCLE' status subscribers found")

            return next_cycle\
                .order_by(Random())\
                .first()

        performed  = subscribers\
            .filter(status=Subscriber.Status.PERFORMED)

        performed_atmost_once = performed\
            .filter(performance_count__lte=1)

        if performed_atmost_once.count() > 0:
            logger.debug(f"{performed_atmost_once.count()} 'PERFORMED - ATLEAST ONCE' subscribers found")
            return performed_atmost_once\
                .order_by(Random())\
                .first()
        else:
            logger.debug(f"{performed.count()} 'PERFORMED - MORE THAN ONCE' status subscribers found")
            return performed\
                .order_by(Random())\
                .first()