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
from .utils import notify_subscriber, update_mailerlite
from .serializers import OpportunitySerializer, OpportunityUpdateSerializer, SubscriberSerializer, SubscriberUpdateSerializer

def discover_opportunities():
    subscribers = Subscriber.objects\
        .filter(artist__is_active=True)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')

    for subscriber in subscribers:
        current_opportunities = Opportunity.objects.filter(subscriber=subscriber)

        if current_opportunities.count() > 0:
            Opportunity\
                .objects\
                .create(
                    concept=subscriber.concept,
                    artist=subscriber.artist,
                    status=Opportunity.POTENTIAL
                )

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def subscribe(request, organization_slug=None, concept_slug=None):
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

                Subscriber.objects.create(concept=concept, artist=artist)

                with transaction.atomic():
                    if settings.IN_PRODUCTION:
                        update_mailerlite(artist, **settings.MAILERLITE)

                    try:
                        notify_subscriber(artist)
                        status = status.HTTP_201_CREATED

                        successful = True
                        messages.success(request, "Your profile was created successfully!")
                    except Exception as e:
                        status = status.HTTP_400_BAD_REQUEST
                        context = {
                            **context,
                            "successful": False,
                            "error": {
                                "message": "Error notifying user"
                            }
                        }
                        
                        messages.error(request, "ERR_N01: An unexpected error occured")
                        if settings.DEBUG:
                            context["e"] = { "type": type(e).__name__, "message": str(e), "args": e.args }

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
def artist_list(_):
    artists = Artist.objects.all()
    return Response([ a.dict() for a in artists ])


@api_view(['GET'])
@permission_classes([AllowAny])
def opportunity_list(_):
    opportunities = Opportunity.objects.all()
    return Response([ o.dict() for o in opportunities ])


@api_view(['GET'])
@permission_classes([AllowAny])
def subscriber_list(_):
    subscribers = Subscriber.objects.all()
    return Response([ s.dict() for s in subscribers ])


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
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
    

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def opportunity_update(request: Request, opportunity_id=None):
    if opportunity_id:
        try:
            data = request.data
            opportunity = Opportunity.objects.get(opportunity_id=opportunity_id)

            serializer = OpportunityUpdateSerializer(instance=opportunity, data=data)
            if serializer.is_valid():
                return Response(
                    data=OpportunitySerializer(instance=serializer.save()).data, 
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


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def subscriber_update(request: Request, subscriber_id=None):
    if subscriber_id:
        try:
            data = request.data
            subscriber =Subscriber.objects.get(subscriber_id=subscriber_id)

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


def home(_):
    concept: Concept = Concept.objects.all().first()
    curator: Curator = concept.curator
    organization: Organization = curator.organization
    
    return redirect(f'/{organization.slug}/{concept.slug}')