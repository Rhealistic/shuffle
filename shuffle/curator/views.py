from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status

from ..artist.models import Opportunity
from . import utils
from .models import Concept, Shuffle, Organization
from .serializers import ShuffleInputSerializer, ShuffleSerializer, OrganizationSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_organizations(_, organization_slug=None):
    orgs = Organization.objects.filter(is_active=True)
    
    if organization_slug:
        try:
            return Response(
                data=OrganizationSerializer(instance=orgs.get()).data, 
                status=drf_status.HTTP_200_OK
            )
        except Organization.DoesNotExist:
            return Response(data={"error": "Organization not found"}, status=drf_status.HTTP_404_NOT_FOUND)
    
    return Response(
        data=OrganizationSerializer(orgs, many=True).data, 
        status=drf_status.HTTP_200_OK
    )


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def do_shuffle(request: Request):
    data = request.data

    if data.get('organization_slug') and data.get('concept_slug'):
        try:
            last_shuffle = Shuffle.objects\
                .filter(concept__slug=data.get('concept_slug'))\
                .filter(concept__curator__organization__slug=data.get('organization_slug'))\
                .filter(closed_at__isnull=True)\
                .latest('created_at')
        except Shuffle.DoesNotExist:
            last_shuffle = None
        
        concept = Concept.objects.get(slug=data.get('concept_slug'))
            
        shuffle = Shuffle.objects.create(
            type=type,
            concept=concept, 
            start_date=timezone.now(),
            last_shuffle=last_shuffle.created_at if last_shuffle else last_shuffle)

        utils.do_shuffle(shuffle)

        return Response(
            data=ShuffleSerializer(instance=shuffle).data, 
            status=drf_status.HTTP_200_OK
        )
    else:
        return Response(
            data={'error': 'Error running Shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def do_reshuffle(request: Request, shuffle_id=None):
    if shuffle_id:
        try:
            shuffle = Shuffle.objects.get(id=shuffle_id)
            
            if request.data.get('status') == "expired":
                invite_status = Opportunity.EXPIRED
            elif request.data.get('status') == "skip":
                invite_status = Opportunity.SKIP
            else:
                invite_status = None
                
            utils.do_reshuffle(shuffle, invite_status=invite_status)

            return Response(
                data={'error': 'Shuffle not found'},
                status=drf_status.HTTP_404_NOT_FOUND
            )
        except Shuffle.DoesNotExist:
            return Response(
                data=ShuffleSerializer(instance=shuffle).data, 
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
    if shuffle_id:
        try:
            data = request.data
            shuffle = Shuffle.objects.get(shuffle_id=shuffle_id)

            serializer = ShuffleInputSerializer(instance=shuffle, data=data)
            if serializer.is_valid():
                serializer.save()

                return Response(
                    data=ShuffleSerializer(instance=serializer.instance).data, 
                    status=drf_status.HTTP_200_OK
                )
            else:
                return Response(
                    data={**serializer.errors, 'error': 'invalid data provided'}, 
                    status=drf_status.HTTP_400_BAD_REQUEST
                )

        except Shuffle.DoesNotExist:
            return Response(
                data={'error': 'Shuffle not found'}, 
                status=drf_status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            data={'error': 'Error updating Shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )
    