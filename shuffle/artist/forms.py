from django.forms import ModelForm

from .models import Artist

class SubscriptionForm(ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'bio',
            'email',
            'phone',
            'photo',
            'instagram',
            'country'
        ]
