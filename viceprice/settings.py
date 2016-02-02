"""
Django settings for viceprice-web project, on Heroku. Fore more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import dj_database_url
import os
from viceprice.constants import *

# NOTE: To set OS environment variables on Heroku, use the command
# heroku config:push -o --filename [settings filepath]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i+acxn5(akgsn!sr4^qgf(^m&*@+g1@u^t@=8s@axc41ml*f=s'

# Database configuration
DATABASES = { 'default': dj_database_url.config(
    default = os.environ.get('DATABASE_URL')
)}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ADMINS = (
    ('Michelle Shu', 'shu.michelle.w@gmail.com'),
    ('Justin Hinh', 'justintsn10@gmail.com')
)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vp'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'viceprice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'viceprice.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'vp', 'static'),
)

# Foursquare
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')

# Amazon Web Services
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

# Mechanical Turk
MTURK_HOST = os.environ.get('MTURK_HOST')

MTURK_HIT_TYPES = {
    FIND_WEBSITE: {
        TITLE: 'Find the official website for a business',
        DESCRIPTION: 'Your goal is to find the official website for a business in Washington, DC',
        ANNOTATION: 'Find website',
        KEYWORDS: ['data collection', 'web search', 'find', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'address'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_WEBSITE'),
        MAX_ASSIGNMENTS: 3,
        MIN_AGREEMENT_PERCENTAGE: 70,
        PRICE: 0.01,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },
    FIND_HAPPY_HOUR_WEB: {
        TITLE: 'Find happy hour info on a website',
        DESCRIPTION: 'Your goal is to search a website for happy hour deals',
        ANNOTATION: 'Find happy hour web',
        KEYWORDS: ['data collection', 'copy', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'url'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_HAPPY_HOUR_WEB'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    }
}