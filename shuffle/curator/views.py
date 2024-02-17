from django.shortcuts import render

from .models import Shuffle

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status

from . import utils
from .models import Concept, Shuffle
from .serializers import ShuffleSerializer

@api_view(['POST'])
def do_shuffle(request: Request, curator_slug: str, concept_slug: str):
    try:
        last_shuffle = Shuffle.objects.filter(slug=concept_slug).latest('created_at')
    except Shuffle.DoesNotExist:
        last_shuffle = None

    data = request.data
    
    concept = Concept.objects.get(slug=concept_slug)
    shuffle = Shuffle(
        concept=concept, 
        last_shuffle=last_shuffle.created_at if last_shuffle else last_shuffle)
    
    utils.do_shuffle(shuffle)

    return ShuffleSerializer(instance=shuffle).data