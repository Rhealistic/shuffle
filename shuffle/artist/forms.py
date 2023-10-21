from django.forms import ModelForm, Textarea

from .models import Artist

class SubscriptionForm(ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'bio',
            'email',
            'phone',
            'instagram'
        ]
        widgets = {
            'bio': Textarea(attrs={'rows': 3}),
        }
