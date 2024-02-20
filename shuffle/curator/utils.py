from django.db.models.functions import Random

from django.utils import timezone

from ..artist.models import Artist, Opportunity
from .models import Shuffle


def do_shuffle(shuffle: Shuffle, status=Opportunity.EXPIRED):
    # 1. On creation, every subscriber has the opportunity_status set to potential
    # 2. On shuffle, the next performer's status is changed to NEXT
    # is set to the performance date, if the last_performance_date is not empty, it means the
    # artist had previously peformed
    #    - Select all subscribers
    #    - If there are no artists in the waiting list, check for previous performers with count 1
    #    - If there are no 
    # 3. 
    assert shuffle.closed_at is None, "The shuffle has already been closed"

    if type == Shuffle.NORMAL:
        return normal_shuffle(
            shuffle, 
            Artist.objects.filter(is_active=True)
        )
    elif type == Shuffle.RESHUFFLE:
        return reshuffle(
            shuffle, 
            Artist.objects.filter(is_active=True),
            status=status
        )


def normal_shuffle(shuffle, subscribers):
    artist: Artist = None

    potentials = subscribers.filter(opportunity__status=Opportunity.POTENTIAL)
    next_cycle = subscribers.filter(opportunity__status=Opportunity.NEXT_CYCLE)
    performed  = subscribers.filter(opportunity__status=Opportunity.PERFORMED)
    performed  = subscribers.filter(opportunity__status=Opportunity.PERFORMED)

    if potentials.count() >=  1:
        artist = potentials.order_by(Random()).first()
    elif next_cycle.count() >=  1:
        artist = next_cycle.order_by(Random()).first()
    elif performed.count() >=  1:
        performed_once = performed.filter(performance_count=1)

        if performed_once.count() >= 1:
            artist = performed_once.order_by(Random()).first()
        else:
            artist = performed.order_by(Random()).first()

    try:
        opportunity = artist.opportunities\
            .filter(
                status=Opportunity.POTENTIAL,
                concept=shuffle.concept
            )\
            .first()
        opportunity.status = Opportunity.WAITING_APPROVAL
        opportunity.save()

    except Opportunity.DoesNotExist:
        opportunity = Opportunity.objects.create(
            concept=shuffle.concept,
            artist=artist,
            status=Opportunity.WAITING_APPROVAL
        )

    artist.selection_count += 1
    artist.save()

    shuffle.chosen = artist
    shuffle.save()

    return artist


def reshuffle(shuffle, artists, status=Opportunity.EXPIRED):
    artist: Artist = None

    try:
        previous: Opportunity = shuffle.chosen\
            .opportunities\
            .filter(concept=shuffle.concept, status=Opportunity.WAITING_APPROVAL)\
            .first()

        previous.status = status
        previous.expired_at = timezone.now()
        previous.artist.save()

        potentials = artists.filter(opportunity__status=Opportunity.POTENTIAL)
        next_cycle = artists.filter(opportunity__status=Opportunity.NEXT_CYCLE)
        performed  = artists.filter(opportunity__status=Opportunity.PERFORMED)

        if potentials.count() >=  1:
            chosen = potentials.order_by(Random()).first()
        elif next_cycle.count() >=  1:
            chosen = next_cycle.order_by(Random()).first()
        elif performed.count() >=  1:
            performed_once = performed.filter(performance_count=1)

            if performed_once.count() >= 1:
                chosen = performed_once.order_by(Random()).first()
            else:
                chosen = performed.order_by(Random()).first()

        opportunity = chosen.opportunities\
            .filter(concept=shuffle.concept)\
            .filter(status=Opportunity.POTENTIAL)\
            .first()
        opportunity.status = Opportunity.WAITING_APPROVAL
        opportunity.save()
    except Opportunity.DoesNotExist:
        opportunity = Opportunity
        
    shuffle.chosen = artist
    shuffle.save()

    return artist