from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status

from shuffle.core.utils import json
from shuffle.curator.models import Concept, Curator, Organization, Shuffle

from .models import Artist, Opportunity, Subscriber
from .forms import SubscriptionForm, ArtistForm
from .utils import create_subscriber
from .serializers import \
    ArtistSerializer, OpportunitySerializer, \
    SubscriberSerializer, SubscriberUpdateSerializer

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def do_subscribe(request: Request, organization_slug:str=None, concept_slug:str=None):
    artist: Artist = None
    start = True
    successful = False
    errors = None
    context = {}
    form = SubscriptionForm()

    try:
        concept = Concept.objects\
            .filter(curator__organization__slug=organization_slug)\
            .filter(slug=concept_slug)\
            .get()

        if request.method == "GET":
            status = drf_status.HTTP_200_OK
        
        elif request.method == "POST":
            form = SubscriptionForm(request.POST, request.FILES)
            
            if form.is_valid():
                artist = form.save()

                create_subscriber(artist, concept)

    except ObjectDoesNotExist as e:
        context = {
            **context,
            'message': "ERR_N404: Object not found"
        }
        status = drf_status.HTTP_404_NOT_FOUND

        messages.error(request, "ERR_404: Concept not found")
    except Exception as e:
        errors = {
            "errors": "500: Server Error"
        }
        status = drf_status.HTTP_500_INTERNAL_SERVER_ERROR

        if settings.DEBUG:
            context["e"] = { 
                "type": type(e).__name__, 
                "message": str(e), "args": e.args 
            }
            messages.error(request, "ERR: An unexpected error occured")
    
    return render(request, "add_subscriber.html", {
        "artist": artist,
        "form": form,
        "errors": errors,
        "start": start,
        "successful": successful,
    }, status=status)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_artist_list(_):
    artists = Artist.objects.all()
    return Response(
        data=ArtistSerializer(artists, many=True).data,
        status=drf_status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_opportunity_list(_, opportunity_id=None):
    opportunities = Opportunity.objects.all()

    if opportunity_id:
        try:
            opportunity = opportunities.get(concept_id=opportunity_id)

            return Response(
                data=OpportunitySerializer(instance=opportunity).data, 
                status=drf_status.HTTP_200_OK
            )
        except Opportunity.DoesNotExist:
            return Response(
                data={"error": "Opportunity NOT Found"}, 
                status=drf_status.HTTP_404_NOT_FOUND)
        
    return Response(
        data=OpportunitySerializer(opportunities, many=True).data,
        status=drf_status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_subscriber_list(_):
    subscribers = Subscriber.objects.all()
    return Response(
        data=SubscriberSerializer(subscribers, many=True).data,
        status=drf_status.HTTP_200_OK
    )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def artist_view(request, artist_id=None):
    artist = Artist.objects.get(artist_id=artist_id)

    data = {}
    if request.method == "POST":
        data = {
            **ArtistSerializer(instance=artist).data,
            **json.loads(request.data)
        }

        form = ArtistForm(data=data, instance=artist)
        if form.is_valid():
            artist = form.save()
            return Response(
                data=ArtistSerializer(instance=artist).data, 
                status=drf_status.HTTP_201_CREATED)
        else:
            data = { "error": "Invalid Input", "message": form.errors }
            return Response(data, status=drf_status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            data=ArtistSerializer(instance=artist).data, 
            status=drf_status.HTTP_200_OK)
    


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def do_subscriber_update(request: Request, subscriber_id=None):
    if subscriber_id:
        try:
            data = request.data
            subscriber = Subscriber.objects.get(subscriber_id=subscriber_id)

            serializer = SubscriberUpdateSerializer(instance=subscriber, data=data)
            if serializer.is_valid():
                return Response(
                    data=SubscriberSerializer(instance=serializer.save()).data, 
                    status=drf_status.HTTP_200_OK
                )
            else:
                return Response(
                    data={**serializer.errors, 'error': 'invalid data provided'}, 
                    status=drf_status.HTTP_400_BAD_REQUEST
                )

        except Shuffle.DoesNotExist:
            return Response(
                data={'error': 'Opportunity not found'}, 
                status=drf_status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            data={'error': 'Error updating Shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )


def go_home(_):
    concept: Concept = Concept.objects.all().first()
    curator: Curator = concept.curator
    organization: Organization = curator.organization
    
    return redirect(f'/subscribe/{organization.slug}/{concept.slug}')