from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status

from shuffle.artist.serializers import OpportunitySerializer

from ..artist.models import Opportunity
from . import utils
from .models import Concept, Shuffle, Organization
from .serializers import \
    ShuffleSerializer, OrganizationSerializer, ConceptSerializer

import logging
logger = logging.getLogger(__name__)

@api_view(["POST"])
def do_discover_opportunities(_, concept_id):
    try:
        concept = Concept.objects\
            .filter(is_active=True)\
            .filter(curator__organization__is_active=True)\
            .filter(curator__is_active=True)\
            .filter(is_active=True)\
            .filter(concept_id=concept_id)\
            .get()
        opportunities = utils.discover_opportunities(concept)

        return Response(
            data=OpportunitySerializer(opportunities, many=True).data, 
            status=drf_status.HTTP_200_OK
        )
    except Concept.DoesNotExist as e:
        logging.exception(e)

        return Response(
            data={'error': 'Concept not found. The concept is either deleted or deactivated'}, 
            status=drf_status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_concepts(_, concept_id=None):
    concepts = Concept.objects\
        .filter(curator__organization__is_active=True)\
        .filter(curator__is_active=True)\
        .filter(is_active=True)\
    
    if concept_id:
        try:
            concept = concepts.get(concept_id=concept_id)

            return Response(
                data=ConceptSerializer(instance=concept).data, 
                status=drf_status.HTTP_200_OK
            )
        except Concept.DoesNotExist as e:
            logging.exception(e)

            return Response(
                data={"error": "Concept NOT Found"}, 
                status=drf_status.HTTP_404_NOT_FOUND)
    
    return Response(
        data=ConceptSerializer(concepts, many=True).data, 
        status=drf_status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_organizations(_, organization_slug=None, organization_id=None):
    organizations = Organization.objects.filter(is_active=True)
    
    if organization_slug or organization_id:
        try:
            organization = organizations\
                .filter(Q(organization_id=organization_id) | Q(organization_slug=organization_slug))\
                .get()

            return Response(
                data=OrganizationSerializer(instance=organization).data, 
                status=drf_status.HTTP_200_OK
            )
        except Organization.DoesNotExist as e:
            logging.exception(e)
            
            return Response(data={"error": "Organization NOT Found"}, status=drf_status.HTTP_404_NOT_FOUND)
    
    return Response(
        data=OrganizationSerializer(organizations, many=True).data, 
        status=drf_status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def do_shuffle(_, concept_id):
    try:
        concept = Concept.objects\
            .filter(curator__organization__is_active=True)\
            .filter(curator__is_active=True)\
            .filter(is_active=True)\
            .filter(concept_id=concept_id)\
            .get()
        opportunity = utils.do_shuffle(concept)

        if opportunity:
            return Response(
                data=OpportunitySerializer(instance=opportunity).data, 
                status=drf_status.HTTP_200_OK
            )
        else:
            return Response(
                data={'error': 'Shuffle could not run at this time. Possible backlog.'}, 
                status=drf_status.HTTP_406_NOT_ACCEPTABLE
            )
    except Exception as e:
        logging.exception(e)

        return Response(
            data={'error': 'Error running shuffle'},
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def do_reshuffle(_, opportunity_id=None, opportunity_status=None):
    try:
        current: Opportunity = Opportunity.objects\
            .filter(status=Opportunity.Status.AWAITING_ACCEPTANCE)\
            .filter(closed_at__isnull=True)\
            .filter(opportunity_id=opportunity_id)\
            .get()

        opportunity = utils.do_reshuffle(current, opportunity_status)

        if opportunity:
            return Response(
                data=OpportunitySerializer(instance=opportunity).data, 
                status=drf_status.HTTP_200_OK
            )
        else:
            return Response(
                data={'error': 'Shuffle could not run.'}, 
                status=drf_status.HTTP_406_NOT_ACCEPTABLE
            )
    except Exception as e:
        logging.exception(e)

        return Response(
            data={'error': 'Error running shuffle'},
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_shuffle(_, shuffle_id=None):
    try:
        shuffle = Shuffle.objects\
            .filter(curator__organization__is_active=True)\
            .filter(curator__is_active=True)\
            .filter(shuffle_id=shuffle_id)\
            .get()
        return Response(
            data=ShuffleSerializer(instance=shuffle).data, 
            status=drf_status.HTTP_200_OK
        )
    except Shuffle.DoesNotExist as e:
        logging.exception(e)

        return Response(
            data={'error': 'Shuffle not found'}, 
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_shuffle_invite(_, opportunity_id=None):
    try:
        opportunity: Opportunity = Opportunity.objects\
            .filter(subscriber__concept__curator__organization__is_active=True)\
            .filter(sent_at__gte=timezone.now() - timedelta(hours=24))\
            .filter(subscriber__concept__curator__is_active=True)\
            .filter(subscriber__concept__is_active=True)\
            .filter(subscriber__is_subscribed=True)\
            .filter(opportunity_id=opportunity_id)\
            .filter(closed_at__isnull=True)\
            .get()
        shuffle = Shuffle.objects\
            .filter(concept__curator__organization__is_active=True)\
            .filter(concept__curator__is_active=True)\
            .filter(concept=opportunity.subscriber.concept)\
            .filter(shuffle_id=opportunity.shuffle_id)\
            .filter(closed_at__isnull=True)\
            .get()

        if utils.accept_invite(shuffle, opportunity):
            return Response(
                data=ShuffleSerializer(instance=shuffle).data, 
                status=drf_status.HTTP_200_OK
            )
        else:
            return Response(
                data=ShuffleSerializer(instance=shuffle).data, 
                status=drf_status.HTTP_200_OK
            )
        
    except Exception as e:
        logging.exception(e)

        return Response(
            data={'error': 'Error updating shuffle'}, 
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
