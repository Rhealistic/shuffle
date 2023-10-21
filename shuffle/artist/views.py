from django.shortcuts import render
from .models import Artist
from .forms import SubscriptionForm

def subscribe(request, *args, **kwargs):
    artist = None
    successful = False

    if request.method == "POST":
        form = SubscriptionForm(request.POST, request.FILES)
        
        if form.is_valid():
            artist = form.save()
            successful = True
    else:
        form = SubscriptionForm()

    return render(request, "add_subscriber.html", {
        'artist': artist,
        'form': form,
        'successful': successful
    })