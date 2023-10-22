import json
import traceback

from .models import Artist
from .forms import SubscriptionForm
from .utils import update_mailerlite, UUIDEncoder

from django.conf import settings
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods


@require_GET
def artist_view(request, artist_id=None, *args, **kwargs):
    artist = Artist.objects.get(artist_id=artist_id)
    artist_dict = model_to_dict(artist, exclude=['id'])
    
    data = json.dumps(
        dict(artist_id=artist.artist_id, **artist_dict), 
        cls=UUIDEncoder, 
        indent=2
    )

    return HttpResponse(data, content_type='application/json')


@require_http_methods(["GET", "POST"])
def subscribe(request, *args, **kwargs):
    artist: Artist = None
    form: SubscriptionForm = None
    successful: bool = False

    if request.method == "POST":
        form = SubscriptionForm(request.POST, request.FILES)
        
        if form.is_valid():
            artist = form.save()
            successful = True

            try:
                if settings.IN_PRODUCTION:
                    update_mailerlite(artist, **settings.MAILERLITE)
            except Exception as e:
                print(traceback.format_exc())

    else:
        form = SubscriptionForm()

    return render(request, "add_subscriber.html", {
        'artist': artist,
        'form': form,
        'successful': successful
    })