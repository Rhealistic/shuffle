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
    

class SMSSendSerializer(serializers.Serializer):
    recipients = serializers.CharField(max_length=15)
    message = serializers.CharField(max_length=480)

    def validate_recipients(self, phone):
        if phone.startswith("0"):
            phone = f"+254{phone[1:]}"

        if not is_valid_phone_number(phone):
            raise serializers.ValidationError("Invalid Safaricom phone Number")
        
        if Artist.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("The phone number is not available")
        
        return phone
    
class AFTSMSSerializer(serializers.Serializer):
    sender_id = serializers.CharField(max_length=50, required=True)
    api_key = serializers.CharField(max_length=100, required=True)
    username = serializers.CharField(max_length=15, required=True)