import base64
import json
import io
import requests

from .models import Site, Post, SiteSerializer
from .forms import ParamsForm, MediaForm, BusinessDetailsForm, SiteForm

from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

def has_yoast_seo(site: Site):
    headers = { 'Authorization': "Basic " + site.encoded_password }

    response = requests\
        .get(f"{site.website_url}wp-json/wp/v2/plugins", headers=headers)

    if response.status_code == 200:
        for plugin in json.dumps(response.json()):
            if plugin['name'] == "Yoast SEO":
                return True
            
    return False

@csrf_exempt
@require_GET
def view_site(request: HttpRequest, site_id: str=None):
    try:
        if site_id is None:
            site: Site = Site.objects.get(site_id=site_id)
            serializer = SiteSerializer(site)

            return JsonResponse(serializer.data)
        else:
            sites: Site = Site.objects.all().order_by('-')
            serializer = SiteSerializer(sites)

            return JsonResponse(serializer.data, many=True)
        
    except ObjectDoesNotExist as e:
        print(e)

    return JsonResponse({
        'error': "Unexpected outcome"
    })

@csrf_exempt
@require_POST
def register_site(request: HttpRequest):
    try:
        page_data = json.loads(request.body)
        form = SiteForm(page_data)

        if form.is_valid():
            site = form.save(commit=False)

            if not site.kyc_done:
                headers = { 'Authorization': "Basic " + site.encoded_password }

                url = f"{site.website_url}wp-json/mm/v1/kyc/update"
                requests.post(
                    url, 
                    headers=headers,
                    json=dict(
                        business_name=form.cleaned_data["business_name"],
                        business_phone_number=form.cleaned_data["business_phone_number"],
                        business_street_address=form.cleaned_data["business_street_address"],
                        business_address_locality=form.cleaned_data["business_address_locality"],
                        business_address_region=form.cleaned_data["business_address_region"],
                        business_postal_code=form.cleaned_data["business_postal_code"],
                        business_country=form.cleaned_data["business_country"]
                    )
                )

                site.wp_business_deets_set = True

            site.save()

        serializer = SiteSerializer(site)
        return JsonResponse(serializer.data)

    except ObjectDoesNotExist as e:
        print(e)

    return JsonResponse({
        'error': "Unexpected outcome"
    })


@csrf_exempt
@require_POST
def create_wordpress_post(request, site_id=None):
    try:
        site: Site = Site.objects.get(site_id=site_id)

        page_data = json.loads(request.body)
        params_form = ParamsForm(page_data)

        data = {}
        if params_form.is_valid():
            media_response = upload_media(
                site, 
                params_form.cleaned_data['media_url'],
                params_form.cleaned_data['title'],
                slugify(params_form.cleaned_data['title']), 
                params_form.cleaned_data['media_alt_text'],
                params_form.cleaned_data['media_caption'],
                params_form.cleaned_data['media_description'])

            if media_response:
                data["featured_media"]  = media_response.get('id')

            headers = { 'Authorization': "Basic " + site.encoded_password }
            data = {
                "title": params_form.cleaned_data['title'],
                "slug": slugify(params_form.cleaned_data['title']),
                "status": params_form.cleaned_data['status'],
                "content": params_form.cleaned_data['content'],
                "meta" : {
                    "seo_title": params_form.cleaned_data['title'],
                    "seo_meta_description": params_form.cleaned_data['meta_description'],
                    "seo_meta_keywords": params_form.cleaned_data['meta_keywords']
                },
                **data
            }

            url = f"{site.website_url}wp-json/wp/v2/posts"
            wp_post = requests\
                .post(url, json=data, headers=headers)\
                .json()
            
            wp_post_id: str = wp_post['id']
            post = Post.objects.create(
                wp_post_id=wp_post_id,
                site=site,
                slug=data['slug'],
                title=data['title'],
                status=data['status'],
                meta_description=data['meta']['seo_meta_description'],
                meta_keywords=data['meta']['seo_meta_keywords'])
            

            return JsonResponse({
                'post_id': post.id,
                'title': post.title,
                'wp_post': wp_post
            })
        else:
            return JsonResponse({
                'error':  {
                    'params': params_form.errors
                }
            })
        
    except ObjectDoesNotExist as e:
        print(e)
        
    return JsonResponse({
        'error': "Unexpected outcome"
    })

def upload_media(
    site:Site, 
    media_url:str, 
    title:str, 
    slug:str=None, 
    media_alt_text:str=None, 
    media_caption:str=None,
    media_description:str=None
):
    headers = {
        'Authorization': "Basic " + site.encoded_password,
    }

    response = requests.post(
        f'{site.website_url}/wp-json/wp/v2/media',
        headers={
            'Content-Type': 'multipart/form-data',
            'Content-Disposition': f'attachment; filename=feature-{slug}.jpg',
            **headers
        },
        data=requests.get(media_url).content
    )

    if response.status_code in (200, 201):
        metadata = {
            "title": title,
            "media_type": "image",
            "alt_text": media_alt_text,
            "caption": media_caption,
            "description": media_description
        }

        media_id = response.json()['id']
        requests.post(
            f'{site.website_url}/wp-json/wp/v2/media/{media_id}',
            headers=headers,
            json=metadata
        )

        return response.json()

@csrf_exempt
@require_POST
def upload_wordpress_media(request, post_id):
    try:
        post = Post.objects.get(post_id=post_id)
        form = MediaForm(json.loads(request.body))
        response = {}

        if form.is_valid():
            media_url = form.cleaned_data['media_url']

            post.media_alt_text = form.cleaned_data['media_alt_text']
            post.media_caption = form.cleaned_data['media_caption']
            post.media_description = form.cleaned_data['media_description']
            post.save()

            media_response = upload_media(
                post.site, 
                media_url, 
                post.title, 
                slug=post.slug, 
                media_alt_text=post.media_alt_text, 
                media_caption=post.media_caption, 
                media_description=post.media_description)

            if media_response.status_code in (201, 200):
                response = {
                    'media': media_response.json()
                }
            else:
                response = {
                    'error': 'Error uploading media'
                }
        else:
            response = {
                'error':  form.errors
            }

    except ObjectDoesNotExist:
        response = {
            'error': 'Post not found'
        }

    return JsonResponse(response)