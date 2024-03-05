import requests
from shuffle.artist.serializers import ShortgyConfigSerializer
from shuffle.curator.models import Config

import logging
logger = logging.getLogger(__name__)

def shorten_url(url):
    logger.debug(f"shorten_url({url})")
    
    try:
        credentials = Config.objects\
            .filter(type=Config.ConfigType.JSON_CONFIG)\
            .filter(key="SHORTGY_CREDENTIALS")\
            .get()\
            .get_json()
        
        if ShortgyConfigSerializer(data=credentials).is_valid():
            logger.debug("config found with valid credentials")

            response = requests\
                .post(
                    "https://api.short.io/links",
                    json={
                        "domain": credentials.get('domain'),
                        "originalURL": url
                    },
                    headers={
                        'Authorization': credentials.get('api_key'),
                    }
                )\
                .json()
            
            logger.debug(response)
            return response.get('secureShortURL') or response.get('shortURL')
        else:
            logger.error("Config is not valid")
    except Config.DoesNotExist as e:
        logger.debug('Encountered an error while shortening url: %s' % str(e))
    except Exception as e:
        logger.debug('Encountered an error while shortening url: %s' % str(e))

