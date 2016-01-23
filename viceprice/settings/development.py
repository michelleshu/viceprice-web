from viceprice.settings.base import *

DATABASES = {'default': dj_database_url.config(
    default='postgres://michelle:w00we!13@localhost:5432/viceprice_development')}

MTURK_HOST = 'mechanicalturk.sandbox.amazonaws.com'

MTURK_HIT_TYPES = {
    FIND_WEBSITE: {
        TITLE: 'Find the official website for a business',
        DESCRIPTION: 'Your goal is to find the official website for a business in Washington, DC',
        ANNOTATION: 'Find website',
        KEYWORDS: ['data collection', 'web search', 'find', 'website'],
        LAYOUT_PARAMETER_NAMES: ['name', 'address'],
        LAYOUT_ID: '3SPZZC8OKQL8Z6QXK6ADEO9RXEGEI2',
        MAX_ASSIGNMENTS: 3,
        MIN_AGREEMENT_PERCENTAGE = 70,
        PRICE: 0.01,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    }
}