from rest_framework import serializers
from .models import Artist, Opportunity

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        exclude = ['id']

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        exclude = ['id']
