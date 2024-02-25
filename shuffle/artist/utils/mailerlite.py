import logging
import json
import requests

from django.db import transaction

from mailerlite import MailerLiteApi
from mailerlite.constants import Subscriber
from uuid import UUID

from ..models import Artist

logger = logging.getLogger(__name__)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)

def update_mailerlite(artist:Artist, api_key:str=None, group_id:str=None):
    if not (api_key or group_id):
        return
    
    data = {
        "email": artist.email,
        "fields": dict(
            name=artist.name,
            artist_id=artist.artist_id.hex
        )
    }

    subscriber: Subscriber = None

    with transaction.atomic():
        api = MailerLiteApi(api_key)
        subscriber = api.subscribers.create(data)
        print("api.subscribers.create", subscriber)

        group = api.groups.add_single_subscriber(group_id, {
            "email": artist.email,
            "name": artist.name,
        })
        print("api.groups.add_single_subscriber", group)

        artist.mailerlite_group_id = group_id
        artist.mailerlite_subscriber_id = subscriber.id
        artist.save()

    return subscriber

def notify_subscriber(artist: Artist):    
    response = requests.post(
        "https://cloud.activepieces.com/api/v1/webhooks/TDpEguqydLUJe4SG2zp7X", data={
            "artist_name": artist.name,
            "phone_number": artist.phone,
            "status": "signup"
        }
    )

    return response.content
