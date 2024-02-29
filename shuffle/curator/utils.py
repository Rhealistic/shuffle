from django.db import transaction
from django.db.models import F
from django.db.models.functions import Random

from django.utils import timezone
from datetime import timedelta

from shuffle.calendar.models import Event

from ..artist.models import Artist, Opportunity, Subscriber
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
                    models.Q(status=Opportunity.Status.ACCEPTED, subscriber__status=Subscriber.Status.PERFORMED, event__status=Event.Status.SUCCESSFUL, last_performance__gte=days_ago(4 * 7)) 
                ) | 
                (
                    models.Q(status=Opportunity.Status.ACCEPTED, event__status_in=[Event.Status.RESCHEDULED, Event.Status.CANCELLED, Event.Status.FAILED], closed_at__gte=days_ago(2 * 7))
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
                    .create(concept=concept,artist=subscriber.artist))
            
    return new_opportunities


def do_shuffle(shuffle: Shuffle):
    with transaction.atomic():
        artist: Artist = pick_performer(shuffle.concept)

        if artist:
            opportunity = Opportunity.objects\
                .filter(subscriber__artist=artist)\
                .filter(subscriber__concept=shuffle.concept)\
                .filter(closed_at__isnull=True)\
                .order_by('-created_at')\
                .first()
            
            if opportunity:
                opportunity.status = Opportunity.Status.AWAITING_ACCEPTANCE
                opportunity.sent_at = timezone.now()
                opportunity.save()

                shuffle.pick = artist
                shuffle.save()

                return opportunity


def do_reshuffle(shuffle: Shuffle, status=Opportunity.Status.EXPIRED):
    with transaction.atomic():
        close_opportunity(shuffle.pick, shuffle.concept, status)
        artist: Artist = pick_performer(shuffle.concept)

        if artist:
            shuffle.pick = artist
            shuffle.retries += 1
            shuffle.save()

            return artist\
                .opportunities\
                .order_by('-created_at')\
                .first()


def pick_performer(concept: Concept):
    with transaction.atomic():
        artists = Artist.objects\
            .filter(is_active=True)\
            .filter(subscription__concept__in=[concept])\
            .filter(subscription__opportunity__closed_at__isnull=True)
        
        potentials = artists.filter(subscription__status=Subscriber.Status.POTENTIAL)
        next_cycle = artists.filter(subscription__status=Subscriber.Status.NEXT_CYCLE)
        performed  = artists.filter(subscription__status=Subscriber.Status.PERFORMED)

        pick: Artist = None

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
        
        Subscriber.objects\
            .filter(artist=pick)\
            .filter(is_subscribed=True)\
            .update(selection_count=F('selection_count') + 1)
        
        return pick


def close_opportunity(artist: Artist, concept:Concept, status:Opportunity.Status):
    with transaction.atomic():
        opportunity: Opportunity = artist\
            .opportunities\
            .filter(subscriber__concept=concept)\
            .filter(closed_at__isnull=True)\
            .order_by('-create_at')\
            .first()

        if opportunity:
            opportunity.status = status
            opportunity.closed_at = timezone.now()
            opportunity.save()
            
            if status == Opportunity.Status.EXPIRED:
                opportunity.subscriber.selection_count += 1
                opportunity.subscriber.save()
            elif status == Opportunity.Status.SKIP:
                opportunity.subscriber.skip_count += 1
                opportunity.subscriber.save()
        
