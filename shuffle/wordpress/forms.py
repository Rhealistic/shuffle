from django import forms
from .models import Site

class ParamsForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea())
    status = forms.CharField(max_length=50)
    tags = forms.CharField(max_length=100, required=False)

    media_url = forms.URLField(required=False)

    media_alt_text = forms.CharField(max_length=300, required=False)
    media_caption = forms.CharField(max_length=300, required=False)
    media_description = forms.CharField(max_length=300, required=False)

    meta_description = forms.CharField(max_length=300)
    meta_keywords = forms.CharField(max_length=300)
    meta_filter = forms.CharField(max_length=300)

class BusinessDetailsForm(forms.Form):
    business_name = forms.CharField(max_length=200)
    business_phone_number = forms.CharField(max_length=25)
    business_street_address = forms.CharField(max_length=100)
    business_address_locality = forms.CharField(max_length=100)
    business_address_region = forms.CharField(max_length=100)
    business_postal_code = forms.CharField(max_length=100)
    business_country = forms.CharField(max_length=10)

class MediaForm(forms.Form):
    media_url = forms.URLField()

    media_alt_text = forms.CharField(max_length=300)
    media_caption = forms.CharField(max_length=300)
    media_description = forms.CharField(max_length=300)

    meta_description = forms.CharField(max_length=300)
    meta_keywords = forms.CharField(max_length=300)
    meta_filter = forms.CharField(max_length=300)


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ['wp_business_deets_set']