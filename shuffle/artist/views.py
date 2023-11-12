from shuffle.core.utils import json
import traceback

from .models import Artist
from .forms import SubscriptionForm, SearchImageForm, ArtistForm
from .utils import update_mailerlite, UUIDEncoder, search_unsplash_photos

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods


@require_GET
@csrf_exempt
def search_image(request):
    data = {}
    form = SearchImageForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['chosen']:
            val = URLValidator()

            try:
                val(form.cleaned_data['chosen'])
                data = {
                    "photo": form.cleaned_data['chosen']
                }
            except ValidationError as e:
                pass
        
        if not data:
            data = search_unsplash_photos(form.cleaned_data['query'])
    else:
        data = {
            'error': 404,
            'message': 'Did you provide a query message?',
            'errors': form.errors
        }

    return JsonResponse(data)

@require_GET
def artist_list(request, artist_id=None, *args, **kwargs):
    artists = Artist.objects.all()
    return JsonResponse([ a.dict() for a in artists ], safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def artist_view(request, artist_id=None, *args, **kwargs):
    artist = Artist.objects.get(artist_id=artist_id)

    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
        form = ArtistForm(data=data, instance=artist)

        if form.is_valid():
            form.save()

            data = json.dumps(
                artist.dict(),
                indent=2)
        else:
            data = {
                "error": "Invalid Input",
                "message": form.errors
            }
    else:
        data = artist.dict()

    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def home(*args, **kwargs):
    return redirect('/santuri/jenga-jungle/')

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