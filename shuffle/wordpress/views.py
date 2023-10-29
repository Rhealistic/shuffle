import base64
import json
import io
import requests

from .models import Site, Post
from .forms import ParamsForm, MediaForm

from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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
@require_POST
def create_wordpress_post(request, site_id=None):
    try:
        site: Site = Site.objects.get(site_id=site_id)
        page_data = json.loads(request.body)

        params_form = ParamsForm(page_data)

        if params_form.is_valid():
            title: str = params_form.cleaned_data['title']
            slug: str = slugify(title)
            status: str = params_form.cleaned_data['status']
            meta_description: str = params_form.cleaned_data['meta_description']
            meta_keywords: str = params_form.cleaned_data['meta_keywords']
            media_url = params_form.cleaned_data.get('media_url')
            media_alt_text = params_form.cleaned_data.get('media_alt_text')
            media_caption = params_form.cleaned_data.get('media_caption')
            media_description = params_form.cleaned_data.get('media_description')
            
            media_response = upload_media(
                site, 
                media_url,
                title, 
                slug, 
                media_alt_text, 
                media_caption, 
                media_description)

            if media_response:
                page_data["featured_media"]  = media_response.get('id')

            headers = { 'Authorization': "Basic " + site.encoded_password }
            post = {
                "slug": slug,
                **page_data,
                **{
                    'meta' : {
                        '_yoast_wpseo_title': title,
                        '_yoast_wpseo_metadesc': meta_description,
                        '_yoast_wpseo_focuskw_text_input': meta_keywords
                    }
                }
            }

            url = f"{site.website_url}wp-json/wp/v2/posts"
            wp_post = requests\
                .post(url, json=post, headers=headers)\
                .json()
            
            wp_post_id: str = wp_post['id']
            post = Post.objects.create(
                site=site,
                slug=slug,
                wp_post_id=wp_post_id,
                title=title,
                status=status,
                meta_description=meta_description,
                meta_keywords=meta_keywords)

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