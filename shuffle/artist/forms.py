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
            'opportunity_status',
            'invite_status',
            'performance_count',
            'next_performance',
            'last_performance'
        ]

    def __init__(self, *args, **kwargs):
        super(ArtistForm, self).__init__(*args, **kwargs)

        self.fields['name'].required = False
        self.fields['bio'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['photo'].required = False
        self.fields['instagram'].required = False
        self.fields['country'].required = False
        self.fields['opportunity_status'].required = False
        self.fields['performance_count'].required = False

class SearchImageForm(forms.Form):
    query = forms.CharField(max_length=150, required=True)
    chosen = forms.CharField(max_length=500, required=False)