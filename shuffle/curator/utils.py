import random

from .models import Shuffle

def do_shuffle(shuffle: Shuffle):
    # 1. On creation, every subscriber has the opportunity_status set to potential
    # 2. On shuffle, the next performer's status is changed to NEXT
    # is set to the performance date, if the last_performance_date is not empty, it means the
    # artist had previously peformed
    #    - Select all subscribers
    #    - If there are no artists in the waiting list, check for previous performers with count 1
    #    - If there are no 
    # 3. 
    from ..artist.models import Artist, Opportunity

    def _shuffle():
        subscribers = Artist.objects.all()

        potentials = subscribers.filter(opportunity__status=Opportunity.POTENTIAL)
        next_cycle = subscribers.filter(opportunity__status=Opportunity.NEXT_PERFORMING)
        performed  = subscribers.filter(opportunity__status=Opportunity.PERFORMED)

        if potentials.count() > 0:
            return random.choice(potentials)
        elif next_cycle.count() > 0:
            return random.choice(next_cycle)
        elif performed.count() > 0:
            performed_once = performed.filter(performance_count__gt=1)

            if performed_once.count() > 0:
                return random.choice(performed_once)
            else:
                return random.choice(performed)


    if type == Shuffle.NORMAL:
        artist: Artist = _shuffle()
        artist.opportunities\
            .filter(status=Opportunity.POTENTIAL)\
            .update(status=Opportunity.WAITING_APPROVAL)
        
        shuffle.chosen = artist
        shuffle.save()

        return artist
    elif type == Shuffle.RESHUFFLE:
        shuffle.chosen\
            .opportunities\
            .filter(concept=shuffle.concept)\
            .update(status=Opportunity.WAITING_APPROVAL)
        return shuffle()

    