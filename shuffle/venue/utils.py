from django.db.models import F
from django.db.models.functions import Random

from django.utils import timezone

from ..artist.models import Artist, Opportunity, Subscriber
from .models import Shuffle


def do_shuffle(shuffle):
    artist: Artist = None
    artists = Artist.objects.filter(is_active=True)
    artist: Artist = find_performer(artists)

    if artist:
        try:
            opportunity = Opportunity.objects\
                .filter(subscriber__artist=artist)\
                .filter(subscriber__concept=shuffle.concept)\
                .filter(status=Opportunity.OpportunityStatus.POTENTIAL)\
                .first()
            
            if opportunity:
                opportunity.invite_status = Opportunity.InviteStatus.WAITING_ACCEPTANCE
                opportunity.save()

        except Opportunity.DoesNotExist:
            opportunity = Opportunity.objects.create(
                concept=shuffle.concept,
                artist=artist,
                invite_status=Opportunity.InviteStatus.WAITING_ACCEPTANCE)

        Subscriber.objects\
            .filter(artist=artist)\
            .filter(is_subscribed=True)\
            .update(selection_count=F('selection_count') + 1)

        shuffle.chosen = artist
        shuffle.save()

    return artist


def do_reshuffle(shuffle: Shuffle, artists, invite_status=Opportunity.InviteStatus.EXPIRED):
    artist: Artist = None

    try:
        previous: Opportunity = shuffle.chosen\
            .opportunities\
            .filter(invite_status=Opportunity.InviteStatus.WAITING_ACCEPTANCE)\
            .filter(concept=shuffle.concept)\
            .first()

        if previous:
            previous.status = invite_status
            previous.expired_at = timezone.now()
            previous.artist.save()
        
        artists = Artist.objects.filter(is_active=True)
        artist: Artist = find_performer(artists)

        if artist:
            opportunity = Opportunity.objects\
                .filter(subscriber__concept=shuffle.concept)\
                .filter(subscriber__artist=artist)\
                .filter(status=Opportunity.OpportunityStatus.POTENTIAL)\
                .first()
        
            if opportunity:
                opportunity.invite_status = Opportunity.InviteStatus.WAITING_ACCEPTANCE
                opportunity.save()

            Subscriber.objects\
                .filter(artist=artist)\
                .filter(is_subscribed=True)\
                .update(selection_count=F('selection_count') + 1)

            shuffle.chosen = artist
            shuffle.retries += 1
            shuffle.save()
    except Opportunity.DoesNotExist:
        opportunity = Opportunity

    return artist

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