from shuffle.core.utils import json
from shuffle.curator.models import Application, Concept
from shuffle.curator.serializers import ApplicationSerializer

from .models import Artist
from .forms import SubscriptionForm, ArtistForm
from .utils import notify_subscriber, update_mailerlite

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


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
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = { "error": "Invalid Input", "message": form.errors }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = artist.dict()
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def subscribe(request, curator_slug=None, concept_slug=None):
    artist: Artist = None

    try:
        concept = Concept.objects.get(
            slug=concept_slug,
            curator__slug=curator_slug
        )

        if request.method == "GET":
            return render(request, "add_subscriber.html", {
                'form': SubscriptionForm(),
                'start': True
            }, status=status.HTTP_200_OK)
        
        elif request.method == "POST":
            form = SubscriptionForm(request.POST, request.FILES)
            
            if form.is_valid():
                artist = form.save()

                with transaction.atomic():
                    if settings.IN_PRODUCTION:
                        update_mailerlite(artist, **settings.MAILERLITE)

                    application = Application\
                        .objects\
                        .create(
                            concept=concept, 
                            artist=artist, 
                            status=Application.PENDING
                        )
                    
                    serializer = ApplicationSerializer(instance=application)

                    if artist.name and artist.phone:
                        try:
                            notify_subscriber(artist)
                            return render(request, "add_subscriber.html", {
                                "artist": serializer.data,
                                "start": False,
                                "form": form,
                                "successful": True
                            }, status=status.HTTP_201_CREATED)
                        except Exception as e:
                            data = {
                                "successful": False,
                                "message": "Error notifying user",
                            }
                            if settings.DEBUG:
                                data["e"] = { "type": type(e).__name__, "message": str(e), "args": e.args }
                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        
            else:
                return Response({
                    "errors": form.errors
                })

    except ObjectDoesNotExist as e:
        return Response({
            "successful": False,
            "errors": ["404: Object not found"],
            "message": "Concept not found",
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        data = {
            "successful": False,
            "errors": "500: Server Error"
        }

        if settings.DEBUG:
            data["e"] = { "type": type(e).__name__, "message": str(e), "args": e.args }

        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def home(request):
    return redirect('/santuri/jenga-jungle/')