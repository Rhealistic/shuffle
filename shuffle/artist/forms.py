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

class SearchImageForm(forms.Form):
    query = forms.CharField(max_length=150, required=True)
    chosen = forms.CharField(max_length=500, required=False)