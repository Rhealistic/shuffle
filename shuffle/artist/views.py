from shuffle.core.utils import json
import traceback

from .models import Artist
from .forms import SubscriptionForm, ArtistForm
from .utils import update_mailerlite

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods


@require_GET
def artist_list(request):
    artists = Artist.objects.all()
    return JsonResponse([ a.dict() for a in artists ], safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def artist_view(request, artist_id=None):
    artist = Artist.objects.get(artist_id=artist_id)

    data = {}
    if request.method == "POST":
        data = {
            **artist.dict(),
            **json.loads(request.body)
        }

        form = ArtistForm(data=data, instance=artist)
        if form.is_valid():
            artist = form.save()
            
            data = json.dumps(artist.dict(), indent=2)
        else:
            data = { "error": "Invalid Input", "message": form.errors }
    else:
        data = artist.dict()

    return JsonResponse(data, safe=False)

@require_http_methods(["GET", "POST"])
def subscribe(request):
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

@require_http_methods(["GET"])
def home(request):
    return redirect('/santuri/jenga-jungle/')