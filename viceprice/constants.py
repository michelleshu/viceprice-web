__author__ = 'michelleshu'
import datetime

'''
constants.py
Common constant values to be used app-wide
'''

# MTurk Stage Names
FIND_WEBSITE = 'FIND_WEBSITE'
FIND_HAPPY_HOUR_WEB = 'FIND_HAPPY_HOUR_WEB'
CONFIRM_HAPPY_HOUR_WEB = 'CONFIRM_HAPPY_HOUR_WEB'
CONFIRM_HAPPY_HOUR_WEB_2 = 'CONFIRM_HAPPY_HOUR_WEB_2'
FIND_HAPPY_HOUR_PHONE = 'FIND_HAPPY_HOUR_PHONE'
CONFIRM_HAPPY_HOUR_PHONE = 'CONFIRM_HAPPY_HOUR_PHONE'
CONFIRM_HAPPY_HOUR_PHONE_2 = 'CONFIRM_HAPPY_HOUR_PHONE_2'
COMPLETE = 'COMPLETE'
NO_INFO = 'NO_INFO'
WRONG_WEBSITE = 'WRONG_WEBSITE'
WRONG_PHONE_NUMBER = 'WRONG_PHONE_NUMBER'

MTURK_STAGE = {
    FIND_WEBSITE: 0,
    FIND_HAPPY_HOUR_WEB: 1,
    CONFIRM_HAPPY_HOUR_WEB: 2,
    CONFIRM_HAPPY_HOUR_WEB_2: 3,
    FIND_HAPPY_HOUR_PHONE: 4,
    CONFIRM_HAPPY_HOUR_PHONE: 5,
    CONFIRM_HAPPY_HOUR_PHONE_2: 6,
    COMPLETE: 7,
    NO_INFO: 8,
    WRONG_WEBSITE: 9,
    WRONG_PHONE_NUMBER: 10
}

# HIT Type Parameters
HIT_TYPE_ID = 'HIT_TYPE_ID'
TITLE = 'TITLE'
DESCRIPTION = 'DESCRIPTION'
ANNOTATION = 'ANNOTATION'
KEYWORDS = 'KEYWORDS'
LAYOUT_PARAMETER_NAMES = 'LAYOUT_PARAMETER_NAMES'
LAYOUT_ID = 'LAYOUT_ID'
MAX_ASSIGNMENTS = 'MAX_ASSIGNMENTS'
PRICE = 'PRICE'
BONUS = 'BONUS'
DURATION = 'DURATION'
US_LOCALE_REQUIRED = 'US_LOCALE_REQUIRED'

# HIT Status
REVIEWABLE = 'Reviewable'

# Assignment Status
SUBMITTED = 'Submitted'
REJECTED = 'Rejected'

# HIT Result Parameters
WEBSITE_FOUND = 'website-found'
WEBSITE_FIELD = 'website'
COMMENTS = 'comments'
HAPPY_HOUR_FOUND = 'happy-hour-found'
DEALS = 'deals'


# Time constants
TIME_FORMATS = ['%H', '%H:%M', '%I:%M%p', '%I%p']

BUSINESS_HOUR_CUTOFF = datetime.time(hour = 20)   # Latest hour to accept for creation of phone HITs

# Maximum number of locations to update at any given time
MAX_LOCATIONS_TO_UPDATE = 100

# Minimum percentage agreement required (e.g. between website URL submissions)
MIN_AGREEMENT_PERCENTAGE = 70.0

# MTurk iteration variables
MAX_ASSIGNMENTS_TO_PUBLISH = 9
MAX_GET_HAPPY_HOUR_WEB_ATTEMPTS = 3
MAX_GET_HAPPY_HOUR_PHONE_ATTEMPTS = 3

# Days it takes for data to expire
EXPIRATION_PERIOD = 30

# Qualifications required of Turkers
MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED = 90
MIN_HITS_COMPLETED = 200

# Days of Week
MONDAY = 'MONDAY'
TUESDAY = 'TUESDAY'
WEDNESDAY = 'WEDNESDAY'
THURSDAY = 'THURSDAY'
FRIDAY = 'FRIDAY'
SATURDAY = 'SATURDAY'
SUNDAY = 'SUNDAY'

DAYS_OF_WEEK = {
    MONDAY: 1,
    TUESDAY: 2,
    WEDNESDAY: 3,
    THURSDAY: 4,
    FRIDAY: 5,
    SATURDAY: 6,
    SUNDAY: 7
}

# Data Sources
WEBSITE = 'WEBSITE'
PHONE = 'PHONE'

DATA_SOURCE = {
    WEBSITE: 1,
    PHONE: 2
}

# Drink Categories
BEER = 'BEER'
WINE = 'WINE'
LIQUOR = 'LIQUOR'

DRINK_CATEGORY = {
    BEER: 1,
    WINE: 2,
    LIQUOR: 3
}

# Deal Detail Data Types
PRICE = 'PRICE'
PERCENT_OFF = 'PERCENT OFF'
PRICE_OFF = 'PRICE OFF'

DEAL_DETAIL_TYPE = {
    PRICE: 1,
    PERCENT_OFF: 2,
    PRICE_OFF: 3
}