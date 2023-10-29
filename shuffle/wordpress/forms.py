from django import forms

class ParamsForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea())
    status = forms.CharField(max_length=100)
    tags = forms.CharField(max_length=100, required=False)

    media_url = forms.URLField(required=False)

    media_alt_text = forms.CharField(max_length=100, required=False)
    media_caption = forms.CharField(max_length=100, required=False)
    media_description = forms.CharField(max_length=200, required=False)

    meta_description = forms.CharField(max_length=200)
    meta_keywords = forms.CharField(max_length=200)
    meta_filter = forms.CharField(max_length=200)

class MediaForm(forms.Form):
    media_url = forms.URLField()

    media_alt_text = forms.CharField(max_length=100)
    media_caption = forms.CharField(max_length=100)
    media_description = forms.CharField(max_length=200)

    meta_description = forms.CharField(max_length=100)
    meta_keywords = forms.CharField(max_length=100)
    meta_filter = forms.CharField(max_length=100)