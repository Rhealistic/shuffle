from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status

from shuffle.artist.serializers import OpportunitySerializer

from ..artist.models import Opportunity

from . import utils
from .models import Concept, Shuffle, Organization
from .serializers import \
    ShuffleInputSerializer, ShuffleSerializer, \
    OrganizationSerializer, ConceptSerializer


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
                .filter(
                    Q(organization_id=organization_id) | 
                    Q(organization_slug=organization_slug))\
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
def do_shuffle(request: Request):
    data = request.data

    if data.get('concept_id'):
        try:
            previous_shuffle = Shuffle.objects\
                .filter(concept__concept_id=data.get('concept_id'))\
                .filter(closed_at__isnull=True)\
                .latest('created_at')
        except Shuffle.DoesNotExist:
            previous_shuffle = None
        
        with transaction.atomic():
            concept = Concept.objects.get(concept_id=data.get('concept_id'))
            shuffle = Shuffle.objects.create(
                concept=concept, 
                start_date=timezone.now(),
                previous_shuffle_id=previous_shuffle.shuffle_id if previous_shuffle else None)

            opportunity = utils.do_shuffle(shuffle)

            if opportunity:
                return Response(
                    data=OpportunitySerializer(instance=opportunity).data, 
                    status=drf_status.HTTP_200_OK
                )
            else:
                shuffle.status = Shuffle.ShuffleStatus.FAILED
                shuffle.closed_at = timezone.now()
                shuffle.save()
            
                return Response(
                    data={'error': 'No artist found for shuffle'}, 
                    status=drf_status.HTTP_404_NOT_FOUND
                )
    else:
        return Response(
            data={'error': 'Error running Shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def do_reshuffle(request: Request, shuffle_id=None):
    if shuffle_id:
        try:
            shuffle = Shuffle.objects.get(id=shuffle_id)
            
            if request.data.get('status') == "expired":
                invite_status = Opportunity.OpportunityStatus.EXPIRED
            elif request.data.get('status') == "skip":
                invite_status = Opportunity.OpportunityStatus.SKIP
            else:
                invite_status = None
                
            with transaction.atomic():
                opportunity = utils.do_reshuffle(shuffle, invite_status=invite_status)
                if opportunity:
                    return Response(
                        data=OpportunitySerializer(instance=opportunity).data, 
                        status=drf_status.HTTP_404_NOT_FOUND
                    )
                else:
                    shuffle.status = Shuffle.ShuffleStatus.FAILED
                    shuffle.closed_at = timezone.now()
                    shuffle.save()

                    return Response(
                        data={'error': 'No artist found for shuffle'}, 
                        status=drf_status.HTTP_404_NOT_FOUND
                    )
        except Shuffle.DoesNotExist:
            return Response(
                data={'error': 'Shuffle not found'},
                status=drf_status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            data={'error': 'Error running re-shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def get_or_update_shuffle(request: Request, shuffle_id=None):
    shuffle: Shuffle = None

    try:
        shuffle = Shuffle.objects.get(shuffle_id=shuffle_id)
    except Shuffle.DoesNotExist:
        return Response(
            data={'error': 'Shuffle not found'}, 
            status=drf_status.HTTP_404_NOT_FOUND
        )

    if request.method == "PUT":
        serializer = ShuffleInputSerializer(instance=shuffle, data=data)
        data = request.data

        if shuffle_id:
            if serializer.is_valid():
                return Response(
                    data=ShuffleSerializer(instance=serializer.save()).data, 
                    status=drf_status.HTTP_200_OK
                )
            else:
                return Response(
                    data={**serializer.errors, 'error': 'invalid data provided'}, 
                    status=drf_status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                data={'error': 'Error updating Shuffle'},
                status=drf_status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            data=ShuffleSerializer(instance=shuffle).data, 
            status=drf_status.HTTP_200_OK
        )

        