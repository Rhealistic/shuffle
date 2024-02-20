from rest_framework import serializers

from .models import \
    Curator, Concept, Shuffle, Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = ['id']

class CuratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curator
        exclude = ['id']


class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        exclude = ['id']


class ShuffleSerializer(serializers.ModelSerializer):
    concept_slug = serializers.StringRelatedField(source='concept.slug')

    class Meta:
        model = Shuffle
        exclude = ['id']


class ShuffleInputSerializer(serializers.Serializer):
    concept_slug = serializers.SlugField()
    concept_slug = serializers.SlugField()