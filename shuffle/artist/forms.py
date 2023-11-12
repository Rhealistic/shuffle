from django import forms

from .models import Artist

class SubscriptionForm(forms.ModelForm):
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
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'bio',
            'email',
            'phone',
            'photo',
            'instagram',
            'country',
            'artist_id',
            'opportunity_status',
            'invite_status',
            'performance_count',
            'next_performance',
            'last_performance'
        ]

class SearchImageForm(forms.Form):
    query = forms.CharField(max_length=150, required=True)
    chosen = forms.CharField(max_length=500, required=False)