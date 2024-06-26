import datetime
import requests

from django.conf import settings
from django.db import models

from shuffle.curator.models import Concept, Config, Curator

from ..models import Artist, Opportunity, Subscriber
from ..serializers import AFTConfigSerializer
from .url_shortener import shorten_url

import logging
logger = logging.getLogger(__name__)


AFRICAS_TALKING_BASE_URL = "https://api.africastalking.com/version1"
AFRICAS_TALKING_MESSAGING_URL = f"{AFRICAS_TALKING_BASE_URL}/messaging"

def send_skip_invite_sms(subscriber: Subscriber):
    logger.debug(f"send_success_sms({subscriber})")
    artist: Artist = subscriber.artist

    config = Config.objects\
        .filter(type=Config.ConfigType.SMS_TEMPLATE)\
        .filter(key="SHUFFLE_SKIP_SMS")\
        .get()
    
    subscriber.sms_count = models.F('sms_count') + 1
    subscriber.save(update_fields=['sms_count'])

    response = send_sms(artist.phone, config.value)
    logger.debug(f"AT's response={response}")


def send_success_sms(subscriber: Subscriber):
    logger.debug(f"send_success_sms({subscriber})")

    artist: Artist = subscriber.artist
    concept: Concept = subscriber.concept
    curator: Curator = concept.curator
    config = Config.objects\
        .filter(type=Config.ConfigType.SMS_TEMPLATE)\
        .filter(key="SHUFFLE_SUCCESS_SMS")\
        .get()
    
    (start, _) = concept.get_next_event_timing()
    message = config.value.format(
        artist_name=artist.name, 
        event_date=start.strftime("%d/%m/%Y"),
        curator_phone=curator.phone
    )
    
    subscriber.sms_count = models.F('sms_count') + 1
    subscriber.save(update_fields=['sms_count'])
    
    response = send_sms(artist.phone, message)
    logger.debug(f"AT's response={response}")


def send_invite_sms(artist: Artist, opportunity: Opportunity, event_date: datetime.datetime):
    logger.debug(f"send_invite_sms({artist.phone})")

    approval_url = shorten_url(f'{settings.BASE_URL}/invite/{opportunity.opportunity_id}/approval/')

    config = Config.objects\
        .filter(type=Config.ConfigType.SMS_TEMPLATE)\
        .filter(key="SHUFFLE_INVITE_SMS")\
        .get()
    
    subscriber: Subscriber = opportunity.subscriber
    concept: Concept = subscriber.concept

    message = config.value.format(
        artist_name=artist.name,
        event_date=event_date.strftime("%d/%m/%Y"),
        event_time=event_date.strftime('%I:%M %p'),
        approval_url=approval_url,
        concept_name=concept.title
    )
    return send_sms(artist.phone, message)


def send_signup_sms(artist: Artist):
    logger.debug(f"send_signup_sms({artist.artist_id}, {artist.phone})")

    config = Config.objects\
        .filter(type=Config.ConfigType.SMS_TEMPLATE)\
        .filter(key="SHUFFLE_SIGNUP_SMS")\
        .get()
    
    return send_sms(artist.phone, config.value.format(artist_name=artist.name))


def send_sms(recipient_phone, message):
    logger.debug(f"send_sms({recipient_phone}, {message})")
    
    try:
        credentials = Config.objects\
            .filter(type=Config.ConfigType.JSON_CONFIG)\
            .filter(key="AFRICAS_TALKING_CREDENTIALS")\
            .get()\
            .get_json()
        
        if AFTConfigSerializer(data=credentials).is_valid():
            logger.debug("config found with valid credentials")

            response = requests.post(
                AFRICAS_TALKING_MESSAGING_URL,
                data={
                    'to': recipient_phone,
                    'from': credentials.get('sender_id'),
                    'username': credentials.get('username'), 
                    'message': message
                },
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'apiKey': credentials.get('api_key'),
                }
            )
            
            logger.debug(response.json())
            return response.json()
        else:
            logger.error("SMS Config is not valid")
    except Config.DoesNotExist as e:
        logger.debug('Encountered an error while sending: %s' % str(e))
    except Exception as e:
        logger.debug('Encountered an error while sending: %s' % str(e))

