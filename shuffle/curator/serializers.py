from rest_framework import serializers

from shuffle.artist.models import Artist
from shuffle.core.utils.helpers import is_valid_phone_number

from .models import \
    Curator, Concept, Shuffle, Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = ['id']

class CuratorSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    
    class Meta:
        model = Curator
        exclude = ['id']


class ConceptSerializer(serializers.ModelSerializer):
    curator = CuratorSerializer()

    class Meta:
        model = Concept
        exclude = ['id']


class ShuffleSerializer(serializers.ModelSerializer):
    concept = ConceptSerializer()

    class Meta:
        model = Shuffle
        exclude = ['id']

    def validate(self, attrs):
        if 'status' not in attrs:
            raise serializers.ValidationError("`status` is required")
        return attrs


class ShuffleInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shuffle
        fields = ['status']

    def validate(self, attrs):
        if 'status' not in attrs:
            raise serializers.ValidationError("`status` is required")
        return attrs
    