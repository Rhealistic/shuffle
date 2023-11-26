from shuffle.core.utils import json

from .models import Artist
from .forms import SubscriptionForm, ArtistForm
from .utils import update_mailerlite

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def artist_list(request):
    artists = Artist.objects.all()
    return Response([ a.dict() for a in artists ])

@csrf_exempt
@api_view(["GET", "POST"])
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
            data = artist.dict()
        else:
            data = { "error": "Invalid Input", "message": form.errors }
    else:
        data = artist.dict()

    return Response(data)

@api_view(["GET", "POST"])
def subscribe(request):
    artist: Artist = None
    form: SubscriptionForm = None
    successful: bool = False

    if request.method == "POST":
        form = SubscriptionForm(request.POST, request.FILES)
        
        if form.is_valid():
            artist = form.save()
            successful = True

            if settings.IN_PRODUCTION:
                update_mailerlite(artist, **settings.MAILERLITE)
        else:
            return Response({
                "errors": form.errors
            })

    else:
        form = SubscriptionForm()

    return render(request, "add_subscriber.html", {
        'artist': artist,
        'form': form,
        'successful': successful
    })

@api_view(['GET'])
def home(request):
    return redirect('/santuri/jenga-jungle/')