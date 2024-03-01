from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status

from shuffle.artist.serializers import OpportunitySerializer
from shuffle.artist.utils.discovery import close_opportunity

from ..artist.models import Opportunity

from . import utils
from .models import Concept, Shuffle, Organization
from .serializers import \
    ShuffleSerializer, OrganizationSerializer, ConceptSerializer


@api_view(["POST"])
def do_discover_opportunities(_, concept_id):
    try:
        concept = Concept.objects\
            .filter(is_active=True)\
            .filter(concept_id=concept_id)\
            .get()
        opportunities = utils.discover_opportunities(concept)

        return Response(
            data=OpportunitySerializer(opportunities, many=True).data, 
            status=drf_status.HTTP_200_OK
        )
    except Concept.DoesNotExist:
        return Response(
            data={'error': 'Concept not found. The concept is either deleted or deactivated'}, 
            status=drf_status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_concepts(_, concept_id=None):
    concepts = Concept.objects.filter(is_active=True)
    
    if concept_id:
        try:
            concept = concepts.get(concept_id=concept_id)

            return Response(
                data=ConceptSerializer(instance=concept).data, 
                status=drf_status.HTTP_200_OK
            )
        except Concept.DoesNotExist:
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
        except Organization.DoesNotExist:
            return Response(data={"error": "Organization NOT Found"}, status=drf_status.HTTP_404_NOT_FOUND)
    
    return Response(
        data=OrganizationSerializer(organizations, many=True).data, 
        status=drf_status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def do_shuffle(_, concept_id):
    try:
        concept = Concept.objects.get(concept_id=concept_id)
        opportunity = utils.do_shuffle(concept)

        if opportunity:
            return Response(
                data=OpportunitySerializer(instance=opportunity).data, 
                status=drf_status.HTTP_200_OK
            )
        else:
            return Response(
                data={'error': 'Shuffle could not run at this time. Possible backlog.'}, 
                status=drf_status.HTTP_400_BAD_REQUEST
            )
    except Exception:
        return Response(
            data={'error': 'Error running shuffle'},
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def do_reshuffle(_, opportunity_id=None, opportunity_status=None):
    try:
        previous: Opportunity = Opportunity.objects\
            .filter(status=Opportunity.Status.PENDING)\
            .filter(closed_at__isnull=True)\
            .get(opportunity_id=opportunity_id)
        
        with transaction.atomic():
            opportunity = utils.do_reshuffle(previous, opportunity_status)

            if opportunity:
                return Response(
                    data=OpportunitySerializer(instance=opportunity).data, 
                    status=drf_status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    data={'error': 'No artist found for shuffle'}, 
                    status=drf_status.HTTP_404_NOT_FOUND
                )
    except Exception:
        return Response(
            data={'error': 'Error running shuffle'},
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_shuffle(_, shuffle_id=None):
    try:
        shuffle = Shuffle.objects.get(shuffle_id=shuffle_id)
        return Response(
            data=ShuffleSerializer(instance=shuffle).data, 
            status=drf_status.HTTP_200_OK
        )
    except Shuffle.DoesNotExist:
        return Response(
            data={'error': 'Shuffle not found'}, 
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def accept_shuffle_invite(_, opportunity_id=None):
    try:
        opportunity: Opportunity = Opportunity.objects.get(opportunity_id=opportunity_id)
        shuffle = Shuffle.objects.get(shuffle_id=opportunity.shuffle_id)

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
        
    except Exception:
        return Response(
            data={'error': 'Error updating shuffle'}, 
            status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
