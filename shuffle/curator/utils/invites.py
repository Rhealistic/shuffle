from django.db import models

from django.utils import timezone
from shuffle.artist.utils.discovery import close_opportunity
from shuffle.artist.utils.sms import send_invite_sms, send_sms, send_success_sms

from shuffle.artist.models import Artist, Opportunity, Subscriber
from ..models import Concept, Config, Shuffle

import logging
logger = logging.getLogger(__name__)


def prepare_invite(shuffle: Shuffle, pick: Subscriber):
    logger.debug(f"prepare_invite({shuffle}, {pick})")

    opportunities = Opportunity.objects\
        .filter(subscriber=pick)\
        .filter(status=Opportunity.Status.PENDING)\
        .filter(closed_at__isnull=True)\
        .order_by('-created_at')
    
    if opportunities.exists():
        opportunity = opportunities.first()
        artist:Artist = opportunity.subscriber.artist
        concept: Concept = pick.concept

        event_date, _ = concept.get_next_event_timing()
        send_invite_sms(artist, event_date)

        logger.debug(f"awaiting acceptance for opportunity ({opportunity})")

        opportunity.status = Opportunity.Status.AWAITING_ACCEPTANCE
        opportunity.sent_at = timezone.now()
        opportunity.shuffle_id = shuffle.shuffle_id
        opportunity.save()

        logger.debug(f"opportunity sent for ({opportunity})")

        shuffle.pick = pick
        shuffle.status = Shuffle.Status.INVITE_SENT
        shuffle.save()

        return opportunity
    else:
        logger.debug(f"Opportunity not found for artist")


def accept_invite(shuffle: Shuffle, opportunity: Opportunity, notes=None):
    logger.debug(f"accept_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.ACCEPTED):
        shuffle.status = Shuffle.Status.COMPLETE
        shuffle.closed_at = timezone.now()
        shuffle.save(update_fields=['status', 'closed_at'])

        if notes:
            opportunity.notes_to_curator = notes
            opportunity.save(update_fields=['notes_to_curator'])

            send_success_sms(opportunity.subscriber)


def skip_invite(shuffle: Shuffle, opportunity: Opportunity):
    logger.debug(f"skip_invite({shuffle}, {opportunity})")

    if close_opportunity(opportunity, Opportunity.Status.SKIP):
        shuffle.pick = None
        shuffle.save(update_fields=['pick'])

        subscriber: Subscriber = opportunity.subscriber
        artist: Artist = subscriber.artist

        config = Config.objects\
            .filter(type=Config.ConfigType.SMS_TEMPLATE)\
            .filter(key="SHUFFLE_SKIP_SMS")\
            .get()
        
        response = send_sms(artist.phone, config.value)
        logger.debug(f"AT's response={response}")

        subscriber.sms_sent = models.F('sms_sent') + 1
        subscriber.save(update_fields=['sms_sent'])