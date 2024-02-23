from rest_framework import serializers
from .models import Artist, Opportunity, Subscriber

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        exclude = ['id']

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        exclude = ['id']


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        exclude = ['id']


class OpportunityUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Opportunity
        fields = [
            'status',
            'invite_status',
            'skipped_at',
            'accepted_at',
            'expired_at',
        ]


class SubscriberUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriber
        fields = [
            'selection_count',
            'acceptance_count',
            'expired_count',
            'skip_count',
            'performance_count',
            'next_performance',
            'last_performance',
            'is_subscribed',
        ]