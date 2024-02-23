from django.db.models.functions import Random

from django.utils import timezone

from ..artist.models import Artist, Opportunity
from .models import Shuffle


def do_shuffle(shuffle):
    artist: Artist = None
    artists = Artist.objects.filter(is_active=True)
    artist: Artist = find_performer(artists)

    if artist:
        try:
            opportunity = Opportunity.objects\
                .filter(artist=artist)\
                .filter(status=Opportunity.POTENTIAL)\
                .filter(concept=shuffle.concept)\
                .first()
            
            if opportunity:
                opportunity.invite_status = Opportunity.WAITING_ACCEPTANCE
                opportunity.save()

        except Opportunity.DoesNotExist:
            opportunity = Opportunity.objects.create(
                concept=shuffle.concept,
                artist=artist,
                invite_status=Opportunity.WAITING_ACCEPTANCE)

        artist.selection_count += 1
        artist.save()

        shuffle.chosen = artist
        shuffle.save()

    return artist


def do_reshuffle(shuffle: Shuffle, artists, invite_status=Opportunity.EXPIRED):
    artist: Artist = None

    try:
        previous: Opportunity = shuffle.chosen\
            .opportunities\
            .filter(concept=shuffle.concept, invite_status=Opportunity.WAITING_ACCEPTANCE)\
            .first()

        if previous:
            previous.status = invite_status
            previous.expired_at = timezone.now()
            previous.artist.save()
        
        artists = Artist.objects.filter(is_active=True)
        chosen: Artist = shuffle(artists)

        if chosen:
            opportunity = Opportunity.objects\
                .filter(concept=shuffle.concept)\
                .filter(artist=chosen)\
                .filter(status=Opportunity.POTENTIAL)\
                .first()
        
            if opportunity:
                opportunity.status = Opportunity.WAITING_APPROVAL
                opportunity.save()

            shuffle.chosen = chosen
            shuffle.retries += 1
            shuffle.save()
    except Opportunity.DoesNotExist:
        opportunity = Opportunity

    return artist

def find_performer(artists):
    potentials = artists.filter(opportunity__status=Opportunity.POTENTIAL)
    next_cycle = artists.filter(opportunity__status=Opportunity.NEXT_CYCLE)
    performed  = artists.filter(opportunity__status=Opportunity.PERFORMED)

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