from django.db import transaction
from django.db.models import F
from django.db.models.functions import Random

from django.utils import timezone
from datetime import timedelta

from ..artist.models import Artist, Opportunity, Subscriber
from .models import Shuffle

from django.db import models
from shuffle.curator.models import Concept


def discover_opportunities(concept: Concept):
    subscribers = Subscriber.objects\
        .filter(artist__is_active=True)\
        .filter(concept=concept)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')
    
    new_opportunities = []

    for subscriber in subscribers:
        # Check if subscriber has meets criteria
        #1. has no pending requests
        #2. Has not accepted / peformed on this platform in the past 1 month
        #3. 
        open_opportunities = Opportunity.objects\
            .filter(subscriber=subscriber)\
            .filter( #in the middle of a shuffle
                (
                    models.Q(invite_status__in=[
                        Opportunity.InviteStatus.PENDING,
                        Opportunity.InviteStatus.SENT,
                        Opportunity.InviteStatus.WAITING_ACCEPTANCE
                    ]) 
                    & 
                    (
                        models.Q(invite_closed_at__isnull=True) | 
                        models.Q(opportunity_closed_at__isnull=True)
                    )
                ) | models.Q(
                    invite_status=Opportunity.InviteStatus.ACCEPTED,
                    invite_closed_at__gte=(timezone.now() - timedelta(days=30.425)) #closed not more than 7 days ago
                ) | models.Q(
                    status=Opportunity.OpportunityStatus.PERFORMED,
                    invite_closed_at__gte=(timezone.now() - timedelta(days=30.425)) #closed not more than 7 days ago
                )
            )
        
        if not open_opportunities.exists():
            new_opportunities.append(
                Opportunity\
                    .objects\
                    .create(
                        concept=concept,
                        artist=subscriber.artist,
                        status=Opportunity.OpportunityStatus.POTENTIAL
                    ))
            
    return new_opportunities


def do_shuffle(shuffle):
    opportunity: Opportunity = None
    artists = Artist.objects.filter(is_active=True)

    with transaction.atomic():
        artist: Artist = find_performer(artists)

        if artist:
            opportunities = Opportunity.objects\
                .filter(subscriber__artist=artist)\
                .filter(subscriber__concept=shuffle.concept)\
                .filter(status=Opportunity.OpportunityStatus.POTENTIAL)\
                .order_by('-created_at')
            if opportunities.exists():
                opportunity = opportunities.first()
                opportunities.update(invite_status=Opportunity.InviteStatus.WAITING_ACCEPTANCE, invite_sent_at=timezone.now())

                Subscriber.objects\
                    .filter(artist=artist)\
                    .filter(is_subscribed=True)\
                    .update(selection_count=F('selection_count') + 1)

                shuffle.chosen = artist
                shuffle.save()

                return opportunity


def do_reshuffle(shuffle: Shuffle, artists, invite_status=Opportunity.InviteStatus.EXPIRED):
    
    with transaction.atomic():
        close_opportunity(shuffle.chosen, shuffle.concept, invite_status)

        artists = Artist.objects.filter(is_active=True)
        artist: Artist = find_performer(artists)

        if artist:
            open_opportunities = Opportunity.objects\
                .filter(subscriber__concept=shuffle.concept)\
                .filter(subscriber__artist=artist)\
                .filter(status=Opportunity.OpportunityStatus.POTENTIAL)\
                .order_by('-created_at')
            
            if open_opportunities.exists():
                opportunity = open_opportunities.first()
                open_opportunities.update(invite_status=Opportunity.InviteStatus.WAITING_ACCEPTANCE)

                Subscriber.objects\
                    .filter(artist=artist)\
                    .filter(is_subscribed=True)\
                    .update(selection_count=F('selection_count') + 1)

                shuffle.chosen = artist
                shuffle.retries += 1
                shuffle.save()

                return opportunity


def find_performer(artists):
    potentials = artists.filter(subscriptions__opportunity__status=Opportunity.OpportunityStatus.POTENTIAL)
    next_cycle = artists.filter(subscriptions__opportunity__status=Opportunity.OpportunityStatus.NEXT_CYCLE)
    performed  = artists.filter(subscriptions__opportunity__status=Opportunity.OpportunityStatus.PERFORMED)

    if potentials.count() > 0:
        return potentials.order_by(Random()).first()
    elif next_cycle.count() > 0:
        return next_cycle.order_by(Random()).first()
    elif performed.count() > 0:
        performed_once = performed.filter(performance_count=1)

        if performed_once.count > 0:
            return performed_once.order_by(Random()).first()
        else:
            return performed.order_by(Random()).first()


def close_opportunity(artist: Artist, concept, invite_status):
    previous: Opportunity = artist\
        .opportunities\
        .filter(invite_status=Opportunity.InviteStatus.WAITING_ACCEPTANCE)\
        .filter(concept=concept)\
        .filter(invite_closed_at__isnull=True)\
        .filter(opportunity_closed_at__isnull=True)

    if previous.exists():
        previous.update(
            status=invite_status,
            invite_closed_at=timezone.now(),
            opportunity_closed_at=timezone.now(),
            outcome_status=Opportunity.OutcomeStatus.FAILED)
        
        subscribers = Subscriber.objects\
            .filter(concept=concept)\
            .filter(artist=artist)
        
        if invite_status == Opportunity.InviteStatus.EXPIRED:
            return subscribers.update(selection_count=F('selection_count') + 1) > 0
        elif invite_status == Opportunity.InviteStatus.SKIP:
            return subscribers.update(selection_count=F('skip_count') + 1) > 0

