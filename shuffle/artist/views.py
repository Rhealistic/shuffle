from shuffle.core.utils import json
from shuffle.curator.models import Concept

from .models import Artist, Opportunity
from .forms import SubscriptionForm, ArtistForm
from .utils import notify_subscriber, update_mailerlite
from .serializers import OpportunitySerializer, ArtistSerializer

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def subscribe(request, curator_slug=None, concept_slug=None):
    artist: Artist = None
    start = True
    successful = False
    errors = None

    try:
        concept = Concept.objects.get(
            slug=concept_slug,
            curator__slug=curator_slug
        )

        if request.method == "GET":
            form = SubscriptionForm()
            status = drf_status.HTTP_200_OK
        
        elif request.method == "POST":
            form = SubscriptionForm(request.POST, request.FILES)
            
            if form.is_valid():
                artist = form.save()

                with transaction.atomic():
                    if settings.IN_PRODUCTION:
                        update_mailerlite(artist, **settings.MAILERLITE)

                    Opportunity\
                        .objects\
                        .create(
                            concept=concept,
                            artist=artist,
                            status=Opportunity.WAITING_APPROVAL
                        )
                    serializer = ArtistSerializer(instance=artist)

                    if artist.name and artist.phone:
                        try:
                            print(notify_subscriber(artist))
                            status = status.HTTP_201_CREATED
                            artist = serializer.data
                            successful = True

                            messages.success("Your profile was created successfully!")

                        except Exception as e:
                            status = status.HTTP_400_BAD_REQUEST
                            data = {
                                "successful": False,
                                "error": {
                                    "message": "Error notifying user"
                                }
                            }
                            
                            messages.error("ERR_N01: An unexpected error occured")
                            if settings.DEBUG:
                                data["e"] = { "type": type(e).__name__, "message": str(e), "args": e.args }

    except ObjectDoesNotExist as e:
        errors = {
            "ERR_N404: Object not found"
        }
        status = drf_status.HTTP_404_NOT_FOUND

        messages.error("ERR_N00: Concept not found")
    except Exception as e:
        errors = {
            "errors": "500: Server Error"
        }
        status = drf_status.HTTP_500_INTERNAL_SERVER_ERROR

        if settings.DEBUG:
            data["e"] = { "type": type(e).__name__, "message": str(e), "args": e.args }
            messages.error("ERR_N00: An unexpected error occured")
    
    return render(request, "add_subscriber.html", {
        "artist": artist,
        "form": form,
        "errors": errors,
        "start": start,
        "successful": successful,
    }, status=status)


@api_view(['GET'])
@permission_classes([AllowAny])
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
            **json.loads(request.data)
        }

        form = ArtistForm(data=data, instance=artist)
        if form.is_valid():
            artist = form.save()
            data = artist.dict()
            return Response(data, status=drf_status.HTTP_201_CREATED)
        else:
            data = { "error": "Invalid Input", "message": form.errors }
            return Response(data, status=drf_status.HTTP_400_BAD_REQUEST)
    else:
        data = artist.dict()
        return Response(data, status=drf_status.HTTP_200_OK)


def home(request):
    return redirect('/santuri/jenga-jungle/')