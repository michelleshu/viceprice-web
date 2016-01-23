__author__ = 'michelleshu'

'''
constants.py
Common constant values to be used app-wide
'''

# MTurk Stage Names
FIND_WEBSITE = 'FIND_WEBSITE'

MTURK_STAGE = {
    FIND_WEBSITE: 0
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
MIN_AGREEMENT_PERCENTAGE = 'MIN_AGREEMENT_PERCENTAGE'
PRICE = 'PRICE'
DURATION = 'DURATION'
US_LOCALE_REQUIRED = 'US_LOCALE_REQUIRED'

# HIT Status
REVIEWABLE = 'Reviewable'

# Assignment Status
SUBMITTED = 'Submitted'
REJECTED = 'Rejected'

# Time constants
TIME_FORMATS = ['%H', '%H:%M', '%I:%M%p', '%I%p']
#BUSINESS_HOUR_CUTOFF = datetime.time(hour=21)   # Latest hour to accept for creation of phone HITs

# Maximum number of locations to update at any given time
MAX_LOCATIONS_TO_UPDATE = 100

# Days it takes for data to expire
EXPIRATION_PERIOD = 30

# Qualifications required of Turkers
MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED = 70
MIN_HITS_COMPLETED = 100

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