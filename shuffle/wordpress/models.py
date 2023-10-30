import rsa
import base64 
import string
import random

from django.conf import settings
from django.db import models

from rest_framework import serializers

def alpha(): 
    return ''.join(
        random.choice(
            string.ascii_uppercase + 
            string.ascii_lowercase + 
            string.digits
        ) 
        for _ in range(32)
    ).lower()

class Site(models.Model):
    site_id = models.CharField(max_length=32, default=alpha)
    
    website_name = models.CharField(max_length=150)
    website_url = models.URLField(unique=True)

    username = models.CharField(max_length=128, null=True)
    password = models.CharField(max_length=128, null=True)

    class Meta:
        db_table = "wordpress_site"


    @property
    def encoded_password(self):
        return base64\
            .b64encode(f'{self.username}:{self.password}'.encode("ascii"))\
            .decode("ascii")
    
    # def set_password(self, password, commit=True):
    #     self.password = rsa.encrypt(
    #         password.encode(), 
    #         settings.WORDPRESS_ENC_PUBLIC_KEY
    #     )

    #     if commit:
    #         self.save()

    # def get_password(self):
    #     return rsa.decrypt(
    #         self.password, 
    #         settings.WORDPRESS_ENC_PRIVATE_KEY
    #     ).decode()
    
class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'

class Post(models.Model):
    site = models.ForeignKey('Site', on_delete=models.SET_NULL, null=True)

    post_id = models.CharField(max_length=32, default=alpha)
    wp_post_id = models.IntegerField(null=True)

    title = models.CharField(max_length=300)
    slug  = models.SlugField(max_length=300, null=True)
    status = models.CharField(max_length=50)

    media_alt_text = models.CharField(max_length=300, null=True)
    media_caption = models.CharField(max_length=300, null=True)
    media_description = models.CharField(max_length=300, null=True)

    meta_description = models.CharField(max_length=300)
    meta_keywords = models.CharField(max_length=300)

    class Meta:
        db_table = "wordpress_post"

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
