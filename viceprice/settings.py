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
database_url = os.environ.get('DATABASE_URL')

DATABASES = {
    'default': dj_database_url.config(default = database_url)
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ADMINS = (
    ('Michelle Shu', 'shu.michelle.w@gmail.com'),
    ('Justin Hinh', 'justin@viceprice.co')
)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'revproxy',
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
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
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

ROLLBAR = {
    'access_token': '31db6b1bdb5c4757abcd5a97e6301098',
    'environment': 'development' if DEBUG else 'production',
    'branch': 'master',
    'root': os.getcwd(),
}

# Foursquare
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')

# Amazon Web Services
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

# Mechanical Turk
MTURK_HOST = os.environ.get('MTURK_HOST')

# Yelp
YELP_CONSUMER_KEY = os.environ.get('YELP_CONSUMER_KEY')
YELP_CONSUMER_SECRET = os.environ.get('YELP_CONSUMER_SECRET')
YELP_TOKEN = os.environ.get('YELP_TOKEN')
YELP_TOKEN_SECRET = os.environ.get('YELP_TOKEN_SECRET')

# Facebook
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
FACEBOOK_APP_TOKEN = os.environ.get('FACEBOOK_APP_TOKEN')

MTURK_HIT_TYPES = {
    FIND_WEBSITE: {
        TITLE: 'Find the website for a business',
        DESCRIPTION: 'Find the official website for a business',
        ANNOTATION: 'Find website',
        KEYWORDS: ['data collection', 'web search', 'find', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'address'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_WEBSITE'),
        MAX_ASSIGNMENTS: 3,
        PRICE: 0.03,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },
    FIND_HAPPY_HOUR_WEB: {
        TITLE: 'Find information on a website',
        DESCRIPTION: 'Search a website for information',
        ANNOTATION: 'Find info web',
        KEYWORDS: ['data collection', 'copy', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'website'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_HAPPY_HOUR_WEB'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },
    CONFIRM_HAPPY_HOUR_WEB: {
        TITLE: 'Check the accuracy of information from a website',
        DESCRIPTION: 'Check the accuracy of information on a website',
        ANNOTATION: 'Confirm info web',
        KEYWORDS: ['data collection', 'copy', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'website', 'deals'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_CONFIRM_HAPPY_HOUR_WEB'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },
    CONFIRM_HAPPY_HOUR_WEB_2: {
        TITLE: 'Check the accuracy of information from a website',
        DESCRIPTION: 'Check the accuracy of information on a website',
        ANNOTATION: 'Confirm info web',
        KEYWORDS: ['data collection', 'copy', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'website', 'deals'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_CONFIRM_HAPPY_HOUR_WEB'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },
    FIND_HAPPY_HOUR_PHONE: {
        TITLE: 'Call a business and find out what specials they are offering. [30 cent bonus for successful calls that get info]',
        DESCRIPTION: 'You will call a business and ask what specials they are offering. You will get a 30 cent bonus for successful calls that get info]',
        ANNOTATION: 'Find business info',
        KEYWORDS: ['phone call', 'phone' 'business info', 'specials', 'bonus'],
        LAYOUT_PARAMETER_NAMES: ['name', 'phone_number'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_HAPPY_HOUR_PHONE'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.10,
        BONUS: 0.30,
        DURATION: 3600,
        US_LOCALE_REQUIRED: True
    },
    CONFIRM_HAPPY_HOUR_PHONE: {
        TITLE: 'Call a business and find out what specials they are offering. [30 cent bonus for successful calls]',
        DESCRIPTION: 'You will call a business, ask what specials they have, and see if our info is up to date [30 cent bonus for successful calls]',
        ANNOTATION: 'Find business info',
        KEYWORDS: ['phone call', 'phone' 'business info', 'specials'],
        LAYOUT_PARAMETER_NAMES: ['name', 'phone_number', 'deals'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_CONFIRM_HAPPY_HOUR_PHONE'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.10,
        BONUS: 0.30,
        DURATION: 3600,
        US_LOCALE_REQUIRED: True
    },
    CONFIRM_HAPPY_HOUR_PHONE_2: {
        TITLE: 'Call a business and find out what specials they are offering. [30 cent bonus for successful calls]',
        DESCRIPTION: 'You will call a business, ask what specials they have, and see if our info is up to date [30 cent bonus for successful calls]',
        ANNOTATION: 'Find business info',
        KEYWORDS: ['phone call', 'phone' 'business info', 'specials'],
        LAYOUT_PARAMETER_NAMES: ['name', 'phone_number', 'deals'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_CONFIRM_HAPPY_HOUR_PHONE'),
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.10,
        BONUS: 0.30,
        DURATION: 3600,
        US_LOCALE_REQUIRED: True
    },
}
