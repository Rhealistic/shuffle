import africastalking
import grequests

from shuffle.curator.models import Config

from ..models import Artist
from ..serializers import AFTSMSSerializer

import logging
logger = logging.getLogger(__name__)

def send_signup_sms(artist: Artist):
    logger.debug(f"send_signup_sms({artist.artist_id}, {artist.phone})")

    return send_sms(artist.phone, (
        f'Shuffle! {artist.name}, thank you for signing up. '
        f'We will communicate via SMS, keep your phone close for opportunities every week.'
    ))


def send_sms(recipient_phone, message):
    logger.debug(f"send_sms({recipient_phone}, {message})")
    
    try:
        config = Config.objects\
            .filter(type=Config.ConfigType.AFRICAS_TALKING_SMS)\
            .get()
        
        if AFTSMSSerializer(data=config.get_value()).is_valid():
            logger.debug("config found with valid credentials")

            africastalking.initialize(
                config.get_value().get('username'), 
                config.get_value().get('api_key')
            )
            sender = config.get_value().get('sender_id')

            response = africastalking\
                .SMS\
                .send(message, [recipient_phone], sender)
            logger.debug(response)

            return response
        else:
            logger.error("SMS Config is not valid")
    except Config.DoesNotExist as e:
        logger.debug('Encountered an error while sending: %s' % str(e))
    except Exception as e:
        logger.debug('Encountered an error while sending: %s' % str(e))