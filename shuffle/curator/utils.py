from django.db import transaction
from django.db.models import F
from django.db.models.functions import Random

from django.utils import timezone
from datetime import timedelta

from shuffle.calendar.models import Event

from ..artist.models import Opportunity, Subscriber
from .models import Shuffle

from django.db import models
from shuffle.curator.models import Concept

days_ago = lambda d: (timezone.now() - timedelta(days=d))

def discover_opportunities(concept: Concept):
    subscribers = concept\
        .concept_subscriptions\
        .filter(artist__is_active=True)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')
    
    new_opportunities = []

    for subscriber in subscribers:
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
            new_opportunities.append(
                Opportunity
                    .objects
                    .create(subscriber=subscriber))
            
    return new_opportunities

def prepare_invite(shuffle: Shuffle, pick: Subscriber):
    opportunity = Opportunity.objects\
        .filter(subscriber=pick)\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .order_by('-created_at')\
        .first()
    
    if opportunity:
        opportunity.status = Opportunity.Status.AWAITING_ACCEPTANCE
        opportunity.sent_at = timezone.now()
        opportunity.shuffle_id = shuffle.shuffle_id
        opportunity.save()

        shuffle.pick = pick
        shuffle.status = Shuffle.Status.INVITE_SENT
        shuffle.save()

        return opportunity


def do_shuffle(concept: Concept):
    with transaction.atomic():
        previous_shuffle = Shuffle.objects\
            .filter(concept=concept)\
            .filter(closed_at__isnull=True)\
            .latest('created_at')
        
        shuffle = Shuffle.objects.create(
            concept=concept, 
            start_date=timezone.now(),
            status=Shuffle.Status.IN_PROGRESS,
            previous_shuffle_id=previous_shuffle.shuffle_id if previous_shuffle else None)
        
        concept.shuffle_count += 1
        concept.save()
        
        r = 0
        while r < 5:
            pick: Subscriber = pick_performer(concept)

            if pick:
                return prepare_invite(shuffle, pick)

            r += 1

        shuffle.status = Shuffle.Status.FAILED
        shuffle.closed_at = timezone.now()
        shuffle.save()


def do_reshuffle(previous: Opportunity):
    with transaction.atomic():
        shuffle = Shuffle.objects\
            .filter(closed_at__isnull=True)\
            .get(shuffle_id=previous.shuffle_id)
        
        shuffle.status = Shuffle.Status.RESHUFFLE
        shuffle.retries += 1
        shuffle.save()

        shuffle.concept.reshuffle_count += 1
        shuffle.concept.save()
    
        r = 0
        while r < 5:
            pick: Subscriber = pick_performer(shuffle.concept)

            if pick:
                return prepare_invite(shuffle, pick)

            r += 1
    
        shuffle.status = Shuffle.Status.FAILED
        shuffle.closed_at = timezone.now()
        shuffle.save()


def pick_performer(concept: Concept):
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
            pick = potentials.order_by(Random()).first()
        elif next_cycle.count() > 0:
            pick = next_cycle.order_by(Random()).first()
        elif performed.count() > 0:
            performed_atmost_once = performed.filter(subscription__performance_count_lte=1)

            if performed_atmost_once.count > 0:
                pick = performed_atmost_once.order_by(Random()).first()
            else:
                pick = performed.order_by(Random()).first()
        
        if pick:
            Subscriber.objects\
                .filter(id=pick.id)\
                .update(selection_count=F('selection_count') + 1)
        
            return pick

