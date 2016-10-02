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
import datetime
from viceprice.constants import *

# NOTE: To set OS environment variables on Heroku, use the command
# heroku config:push -o --filename [settings filepath]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i+acxn5(akgsn!sr4^qgf(^m&*@+g1@u^t@=8s@axc41ml*f=s'

# Database configuration
database_url = os.environ.get('DATABASE_URL')


# Justin's production Database URL. DO NOT USE.
#database_url = "postgres://catdnlfxohubob:kCb_lR4zUIb4IVYqccmyj83kpi@ec2-54-227-254-13.compute-1.amazonaws.com:5432/d478v5mn7g8jnq"

DATABASES = {
    'default': dj_database_url.config(default = database_url)
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False


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
    'django.middleware.security.SecurityMiddleware'
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

# Yelp
YELP_CONSUMER_KEY = os.environ.get('YELP_CONSUMER_KEY')
YELP_CONSUMER_SECRET = os.environ.get('YELP_CONSUMER_SECRET')
YELP_TOKEN = os.environ.get('YELP_TOKEN')
YELP_TOKEN_SECRET = os.environ.get('YELP_TOKEN_SECRET')

# Facebook
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
FACEBOOK_APP_TOKEN = os.environ.get('FACEBOOK_APP_TOKEN')

# Maximum number of locations to update at any given time
MAX_LOCATIONS_TO_UPDATE = 100

# MTurk iteration variables
MAX_ASSIGNMENTS_TO_PUBLISH = 9      # Max total assignments to publish for one HIT
MIN_RESPONSES = 3                   # Min number of responses to accept
MIN_AGREEMENT_PERCENTAGE = 70       # Percentage of HIT responses that need to agree before we accept the result

# Days it takes for data to expire
EXPIRATION_PERIOD = 30

# Qualifications required of Turkers
MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED = 90
MIN_HITS_COMPLETED = 100

MTURK_HIT_TYPES = {
    FIND_HAPPY_HOUR: {
        TITLE: 'Find, copy, and paste information from a website',
        DESCRIPTION: 'You will be given a url. Go to it and search for a specific deal offered by the business.',
        ANNOTATION: 'Find info',
        KEYWORDS: ['survey', 'data', 'website', 'search', 'data collection', 'url', 'simple', 'data entry', 'copy and paste', 'website search', 'find', 'listings', 'web', 'information', 'info', 'entry'],
        LAYOUT_PARAMETER_NAMES: ['name', 'website'],
        LAYOUT_ID: os.environ.get('HIT_LAYOUT_ID_FIND_HAPPY_HOUR'),
        MAX_ASSIGNMENTS: 3,
        PRICE: 0.05,
        BONUS: 0.0,
        LIFETIME: datetime.timedelta(21),
        DURATION: 3600,
        LOCALE_REQUIRED: 'US'
    }
}

MTURK_TEST_MODE = False