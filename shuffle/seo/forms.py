from django import forms

class NotifyIndexerForm(forms.Form):
    url_to_index = forms.URLField()
