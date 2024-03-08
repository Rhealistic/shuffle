"""
Django settings for shuffle project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import colorlog
from pathlib import Path

import dj_database_url
from dotenv import dotenv_values

config = dotenv_values()

try:
   import pymysql
   pymysql.version_info = (1, 4, 6, 'final', 0)
   pymysql.install_as_MySQLdb()
except ImportError:
   pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('SECRET_KEY', 'django-insecure-#(n4a!k6vsoi-f-p-2iwd3ru$c#+q9qagbs767ye7(7=fhr3@!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = config.get('ALLOWED_HOSTS', "").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework'
]

INSTALLED_APPS += [
   x.strip() for x in config.get('INSTALLED_APPS', "").split(",")
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = config.get('ROOT_URLCONF', 'shuffle.urls')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shuffle.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if config.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        default=config.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = config.get('TIME_ZONE', 'UTC')

USE_L10N = True
USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = config.get('STATIC_URL', 'static/')
STATIC_ROOT = config.get('STATIC_ROOT', os.path.join(BASE_DIR, 'static_root'))

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#---------

IN_PRODUCTION = not DEBUG
MAILERLITE = {
   "api_key": config.get('MAILERLITE_API_KEY', "mailerlite_api_key"),
   "group_id": config.get('MAILERLITE_GROUP_ID', "mailerlite_subscriber_group_id"),
}

ADMIN_KEY = config.get('ADMIN_KEY', 'admin-key')
UNSPLASH_API_KEY = config.get('UNSPLASH_API_KEY', '<UNSPLASH_API_KEY>')

WORDPRESS_ENC_PUBLIC_KEY = config.get('WORDPRESS_ENC_PUBLIC_KEY', '<WORDPRESS_ENC_PUBLIC_KEY>')
WORDPRESS_ENC_PRIVATE_KEY = config.get('WORDPRESS_ENC_PRIVATE_KEY', '<WORDPRESS_ENC_PRIVATE_KEY>')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.BasicAuthentication',
        'shuffle.core.auth.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ],
}

if config.get('ENVIRONMENT', 'production') == 'production':
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer'
    ]
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'colored_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'formatters': {
        'colored': {
            '()': colorlog.ColoredFormatter,
            'format': "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'log_colors': {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
        },
    },
    'loggers': {
        '': {
            'handlers': ['colored_console'],
            'level': 'DEBUG',
        },
    },
}

BASE_URL = "https://shuffle.rhealistic.info"
BASE_API_URL = f"{BASE_URL}/v1"