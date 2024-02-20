from django.shortcuts import render


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status

from ..artist.models import Opportunity
from . import utils
from .models import Concept, Shuffle, Organization
from .serializers import ShuffleSerializer, OrganizationSerializer


@api_view(['GET'])
def organizations(_, organization_slug=None):
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


@api_view(['POST'])
def do_shuffle(request: Request):
    if (
        request.data.get('shuffle_type') in ('reshuffle', 'normal') and
        request.data.get('organization_slug') and
        request.data.get('concept_slug') and 
        request.data.get('status') in ('skip', 'expired')
    ):
        try:
            last_shuffle = Shuffle.objects\
                .filter(
                    slug=request.data.get('concept_slug'), 
                    concept__organization__slug=request.data.get('organization_slug')
                )\
                .latest('created_at')
        except Shuffle.DoesNotExist:
            last_shuffle = None
        
        concept = Concept.objects.get(slug=request.data.get('concept_slug'))
        type = Shuffle.NORMAL if request.data.get('shuffle_type') == "normal" else Shuffle.RESHUFFLE
        shuffle = Shuffle.objects.create(
            type=type,
            concept=concept, 
            last_shuffle=last_shuffle.created_at if last_shuffle else last_shuffle)

        status = (Opportunity.EXPIRED if request.data.get('status') == "expired" else Opportunity.SKIP)
        utils.do_shuffle(shuffle, status=status)

        return Response(
            data=ShuffleSerializer(instance=shuffle).data, 
            status=drf_status.HTTP_200_OK
        )
    else:
        return Response(
            data={'error': 'Error running Shuffle'},
            status=drf_status.HTTP_400_BAD_REQUEST
        )

