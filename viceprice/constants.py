__author__ = 'michelleshu'

'''
constants.py
Common constant values to be used app-wide
'''

# MTurk Stage Names
FIND_WEBSITE = 'FIND_WEBSITE'
FIND_HAPPY_HOUR_WEB = 'FIND_HAPPY_HOUR_WEB'
CONFIRM_HAPPY_HOUR_WEB = 'CONFIRM_HAPPY_HOUR_WEB'
FIND_HAPPY_HOUR_PHONE = 'FIND_HAPPY_HOUR_PHONE'
CONFIRM_HAPPY_HOUR_PHONE = 'CONFIRM_HAPPY_HOUR_PHONE'
COMPLETE = 'COMPLETE'
NO_INFO = 'NO_INFO'

MTURK_STAGE = {
    FIND_WEBSITE: 0,
    FIND_HAPPY_HOUR_WEB: 1,
    CONFIRM_HAPPY_HOUR_WEB: 2,
    FIND_HAPPY_HOUR_PHONE: 3,
    CONFIRM_HAPPY_HOUR_PHONE: 4,
    COMPLETE: 5,
    NO_INFO: 6
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
DURATION = 'DURATION'
US_LOCALE_REQUIRED = 'US_LOCALE_REQUIRED'

# HIT Status
REVIEWABLE = 'Reviewable'

# Assignment Status
SUBMITTED = 'Submitted'
REJECTED = 'Rejected'

# HIT Result Parameters
URL_FOUND = 'url-found'
URL = 'url'
COMMENTS = 'comments'
HAPPY_HOUR_FOUND = 'happy-hour-found'
MONDAY_START_TIME = 'monday-start-time'
MONDAY_END_TIME = 'monday-end-time'
MONDAY_DESCRIPTION = 'monday-description'
TUESDAY_START_TIME = 'tuesday-start-time'
TUESDAY_END_TIME = 'tuesday-end-time'
TUESDAY_DESCRIPTION = 'tuesday-description'
WEDNESDAY_START_TIME = 'wednesday-start-time'
WEDNESDAY_END_TIME = 'wednesday-end-time'
WEDNESDAY_DESCRIPTION = 'wednesday-description'
THURSDAY_START_TIME = 'thursday-start-time'
THURSDAY_END_TIME = 'thursday-end-time'
THURSDAY_DESCRIPTION = 'thursday-description'
FRIDAY_START_TIME = 'friday-start-time'
FRIDAY_END_TIME = 'friday-end-time'
FRIDAY_DESCRIPTION = 'friday-description'
SATURDAY_START_TIME = 'saturday-start-time'
SATURDAY_END_TIME = 'saturday-end-time'
SATURDAY_DESCRIPTION = 'saturday-description'
SUNDAY_START_TIME = 'sunday-start-time'
SUNDAY_END_TIME = 'sunday-end-time'
SUNDAY_DESCRIPTION = 'sunday-description'


# Time constants
TIME_FORMATS = ['%H', '%H:%M', '%I:%M%p', '%I%p']
#BUSINESS_HOUR_CUTOFF = datetime.time(hour=21)   # Latest hour to accept for creation of phone HITs

# Maximum number of locations to update at any given time
MAX_LOCATIONS_TO_UPDATE = 100

# Minimum percentage agreement required (e.g. between website URL submissions)
MIN_AGREEMENT_PERCENTAGE = 70.0

# Maximum number of assignments to publish
MAX_ASSIGNMENTS_TO_PUBLISH = 9

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