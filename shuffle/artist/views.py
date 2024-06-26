from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseServerError
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status
from shuffle.artist.utils.sms import send_signup_sms, send_sms
from shuffle.calendar.utils import hours_ago

from shuffle.core.utils import json
from shuffle.curator.models import Concept, Curator, Organization, Shuffle
from shuffle.curator.utils import accept_invite, do_reshuffle, skip_invite

from .models import Artist, Opportunity, Subscriber
from .forms import \
    ApproveOpportunityForm, RejectOpportunityForm, SubscriptionForm, ArtistForm
from .serializers import \
    ArtistSerializer, OpportunitySerializer, SMSSendSerializer, \
    SubscriberSerializer, SubscriberUpdateSerializer

import logging
logger = logging.getLogger(__name__)

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def do_subscribe(request: Request, organization_slug:str=None, concept_slug:str=None):
    artist: Artist = None
    successful = False
    form = SubscriptionForm()
    status = drf_status.HTTP_200_OK
    concept = None

    try:
        concept = Concept.objects\
            .filter(curator__organization__slug=organization_slug)\
            .filter(slug=concept_slug)\
            .get()

        if request.method == "POST":
            form = SubscriptionForm(request.POST, request.FILES)
            
            if form.is_valid():
                logger.info("Subscription form is valid")

                subscriber = Subscriber.objects\
                    .create(concept=concept, artist=form.save())

                response = send_signup_sms(subscriber.artist)
                logger.debug(f"Sending SMS: {response}")
                
                status = drf_status.HTTP_201_CREATED
                successful = True

        return render(request, "add_subscriber.html", {
            "artist": artist,
            "form": form,
            "organization": concept.curator.organization,
            "concept": concept,
            "successful": successful,
        }, status=status)

    except ObjectDoesNotExist as e:
        status = drf_status.HTTP_404_NOT_FOUND
        return HttpResponseNotFound()
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()

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
            opportunity = opportunities\
                .get(opportunity_id=opportunity_id)
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
    
    return redirect(
        reverse('subscribe-to-concept', args=(
            organization.slug, concept.slug
        ))
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def sms_send(request, artist_id):
    logger.debug("request received: sms_send")
    logger.debug(request.data)

    try:
        serializer = SMSSendSerializer(data=request.data)
        artist = Artist.objects\
            .filter(artist_id=artist_id)\
            .get()

        if serializer.is_valid():
            logger.debug("SMS: Sending sms to recipient")
            response = send_sms(
                artist.phone, 
                serializer.validated_data['message']
            )

            logger.debug("SMS: send response.")
            return Response(
                data=response, 
                status=drf_status.HTTP_200_OK
            )
        else:
            logger.debug("SMS: Data received is invalid.")
            logger.debug(serializer.errors)

            return Response(
                data={
                    **serializer.errors,
                    "error": "Error sending SMS.",
                }, 
                status=drf_status.HTTP_400_BAD_REQUEST
            )
    except Artist.DoesNotExist:
        return Response(
                data={
                    "error": "Error sending SMS.",
                }, 
                status=drf_status.HTTP_404_NOT_FOUND
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def sms_delivery(request):
    logger.debug("<SMS DELIVERY>")

    logger.debug(request.data)

    logger.debug("</SMS DELIVERY>")
    return Response(
        data={"received": True},
        status=drf_status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def sms_optout(request):
    logger.debug("<SMS OPT OUT>")

    logger.debug(request.data)

    logger.debug("</SMS OPT OUT>")
    return Response(
        data={"received": True},
        status=drf_status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def sms_optin(request):
    logger.debug("<SMS OPT IN>")

    logger.debug(request.data)

    logger.debug("</SMS OPT IN>")
    return Response(
        data={"received": True},
        status=drf_status.HTTP_200_OK
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def invitation_approval(request: Request, opportunity_id:str=None):
    try:
        opportunity: Opportunity = Opportunity.objects\
            .filter(subscriber__concept__curator__organization__is_active=True)\
            .filter(subscriber__concept__curator__is_active=True)\
            .filter(subscriber__concept__is_active=True)\
            .filter(subscriber__is_subscribed=True)\
            .filter(opportunity_id=opportunity_id)\
            .filter(sent_at__gte=hours_ago(24))\
            .filter(closed_at__isnull=True)\
            .get()

        return render(request, "invitation.html", {
            'opportunity': opportunity
        })
    except ObjectDoesNotExist as e:
        logger.exception(e)

        return HttpResponseNotFound()
    except Exception as e:
        logger.exception(e)

        return HttpResponseServerError()


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def do_approve(request: Request, opportunity_id:str=None, action:Opportunity.Status=None):
    try:
        opportunity: Opportunity = Opportunity.objects\
            .filter(subscriber__concept__curator__organization__is_active=True)\
            .filter(subscriber__concept__curator__is_active=True)\
            .filter(subscriber__concept__is_active=True)\
            .filter(subscriber__is_subscribed=True)\
            .filter(opportunity_id=opportunity_id)\
            .filter(sent_at__gte=hours_ago(24))\
            .filter(closed_at__isnull=True)\
            .get()
        shuffle = Shuffle.objects\
            .filter(concept=opportunity.subscriber.concept)\
            .filter(shuffle_id=opportunity.shuffle_id)\
            .filter(closed_at__isnull=True)\
            .get()


        if action == Opportunity.Status.ACCEPTED:
            if request.method == "POST":
                form: ApproveOpportunityForm = ApproveOpportunityForm(request.POST)

                if form.is_valid():
                    with transaction.atomic():
                        if accept_invite(shuffle, opportunity, notes=form.cleaned_data['notes_to_curator']):
                            organization: Organization = opportunity.subscriber.concept.curator.organization
                            return redirect(organization.website)
            else:
                form: ApproveOpportunityForm = ApproveOpportunityForm()
        elif action == Opportunity.Status.SKIP:
            if request.method == "POST":
                form: RejectOpportunityForm = RejectOpportunityForm(request.POST)

                if form.is_valid():
                    with transaction.atomic():
                        if skip_invite(shuffle, opportunity, **form.cleaned_data):
                            organization: Organization = opportunity.subscriber.concept.curator.organization
                            return redirect(organization.website)
            else:
                form = RejectOpportunityForm()
        
        return render(request, "approval.html", {
            'opportunity': opportunity,
            'action': action,
            'form': form
        })
    except ObjectDoesNotExist as e:
        logger.exception(e)

        return HttpResponseNotFound()
    except Exception as e:
        logger.exception(e)

        return HttpResponseServerError()

