from django import forms

from shuffle.core.utils.helpers import is_valid_phone_number

from .models import Artist, Opportunity


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
        ]


class ApproveOpportunityForm(forms.Form):
    notes_to_curator = forms.CharField(
        label="Notes to curator (optional)",
        required=False,
        max_length=250,
        widget=forms.Textarea(attrs={
            "class": "special", 
            "placeholder": (
                "Any special notes to the curator on what Santuri gear "
                "you are interested in. Please note, you can bring your own gear."
            ),
            "rows": "5"
        }))
    
class RejectOpportunityForm(forms.Form):
    reason = forms.ChoiceField(
        label="Reason (optional)",
        choices=Opportunity.RejectReason.choices)
    notes_to_curator = forms.CharField(
        label="Notes to curator (optional)",
        required=False,
        max_length=250,
        widget=forms.Textarea(attrs={
            "class": "special", 
            "placeholder": (
                "You can give a small note of apology as a reason for the skipping of the opportunity."
            ),
            "rows": "5"
        }))