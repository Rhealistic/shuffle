from datetime import timedelta
from django.utils import timezone
from shuffle.artist.utils.discovery import close_opportunity
from shuffle.artist.utils.sms import \
    send_invite_sms, \
    send_skip_invite_sms, \
    send_success_sms

from shuffle.artist.models import Artist, Opportunity, Subscriber
from shuffle.calendar.utils import hours_ago
from ..models import Concept, Shuffle

import logging
logger = logging.getLogger(__name__)


def fetch_expired_shuffle_invites():
    return Opportunity.objects\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .filter(sent_at__lte=hours_ago(24))\


def prepare_invite(shuffle: Shuffle, pick: Subscriber) -> Opportunity:
    logger.debug(f"prepare_invite({shuffle}, {pick})")

    opportunity = Opportunity.objects\
        .filter(subscriber=pick)\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .order_by('-created_at')\
        .first()
    
    if opportunity:
        artist:Artist = opportunity.subscriber.artist
        concept: Concept = pick.concept

        logger.debug(f"awaiting acceptance for opportunity ({opportunity})")

        opportunity.status = Opportunity.Status.AWAITING_ACCEPTANCE
        opportunity.sent_at = timezone.now()
        opportunity.shuffle_id = shuffle.shuffle_id
        opportunity.save()

        logger.debug(f"opportunity sent for ({opportunity})")

        shuffle.pick = pick
        shuffle.status = Shuffle.Status.INVITE_SENT
        shuffle.save()

        event_date, _ = concept.get_next_event_timing()
        send_invite_sms(artist, opportunity, event_date)

        return opportunity
    else:
        logger.debug(f"Opportunity not found for artist")


def accept_invite(shuffle: Shuffle, opportunity: Opportunity, notes=None) -> bool:
    logger.debug(f"accept_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.ACCEPTED):
        shuffle.status = Shuffle.Status.COMPLETE
        shuffle.closed_at = timezone.now()
        shuffle.save(update_fields=['status', 'closed_at'])

        if notes:
            opportunity.notes_to_curator = notes
            opportunity.save(update_fields=['notes_to_curator'])

            send_success_sms(opportunity.subscriber)
            return True


def skip_invite(shuffle: Shuffle, opportunity: Opportunity, reason=None, notes_to_curator=None) -> bool:
    logger.debug(f"skip_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.SKIP):
        shuffle.pick = None
        shuffle.save(update_fields=['pick'])

        opportunity.reject_reason = reason
        opportunity.notes_to_curator = notes_to_curator
        opportunity.save(update_fields=['notes_to_curator', 'reject_reason'])

        from shuffle.curator.utils import do_reshuffle
        do_reshuffle(opportunity, Opportunity.Status.SKIP)
        
        send_skip_invite_sms(opportunity.subscriber)
        return True

