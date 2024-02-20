from django import forms

from shuffle.core.utils.helpers import is_valid_phone_number

from .models import Artist

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'bio',
            'email',
            'phone',
            'instagram',
            'mixcloud',
            'soundcloud',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone: str = self.cleaned_data['phone']

        if phone.startswith("0"):
            phone = f"+254{phone[1:]}"

        if Artist.objects.filter(phone=phone).exists():
            raise forms.ValidationError("The phone number is in use")

        if not is_valid_phone_number(phone):
            raise forms.ValidationError("Invalid Safaricom phone Number")
        
        return phone

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'bio',
            'email',
            'phone',
            'photo',
            'mixcloud',
            'soundcloud',
            'instagram',
            'country',
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
        self.fields['performance_count'].required = False

class SearchImageForm(forms.Form):
    query = forms.CharField(max_length=150, required=True)
    chosen = forms.CharField(max_length=500, required=False)