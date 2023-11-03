import json
import requests

from .forms import NotifyIndexerForm
from shuffle.wordpress.models import Site
from .utils import notify_google_indexing

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

@csrf_exempt
@require_http_methods(["GET", "POST"])
def notify_indexer(request: HttpRequest, site_id=None):
    try:
        site: Site = Site.objects.get(site_id=site_id)

        if request.method == "POST":
            page_data = json.loads(request.body)
            form = NotifyIndexerForm(page_data)

            if form.is_valid():
                notify_google_indexing(
                    site,
                    form.cleaned_data['url_to_index']
                )

        return JsonResponse({
            "business_name": site.business_name
        })
    except ObjectDoesNotExist as e:
        print(e)
        
    return JsonResponse({
        'error': "Unexpected outcome"
    })