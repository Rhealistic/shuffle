from rest_framework import serializers

from .models import \
    Curator, Concept, Shuffle


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
