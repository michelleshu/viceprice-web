__author__ = 'michelleshu'

import datetime
from viceprice import settings

# Connection constants
ACCESS_ID = 'AKIAJUOZ7FVQMBTEZPQA'
SECRET_KEY = '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'
HOST = 'mechanicalturk.amazonaws.com'

# HIT Type parameters
HIT_TYPE_ID = 'HIT_TYPE_ID'
TITLE = 'TITLE'
DESCRIPTION = 'DESCRIPTION'
ANNOTATION = 'ANNOTATION'
LAYOUT_PARAMETER_NAMES = 'LAYOUT_PARAMETER_NAMES'
LAYOUT_ID = 'LAYOUT_ID'
MAX_ASSIGNMENTS = 'MAX_ASSIGNMENTS'
PRICE = 'PRICE'
DURATION = 'DURATION'
US_LOCALE_REQUIRED = 'US_LOCALE_REQUIRED'

# HIT Type names
VERIFY_WEBSITE = 'VERIFY_WEBSITE'
FIND_WEBSITE_HH_B = 'FIND_WEBSITE_HH'
CONFIRM_WEBSITE_HH_B = 'CONFIRM_WEBSITE_HH'
FIND_PHONE_HH = 'FIND_PHONE_HH'
CONFIRM_PHONE_HH = 'CONFIRM_PHONE_HH'
CATEGORIZE = 'CATEGORIZE'
COMPLETE = 'COMPLETE'
NO_HH_FOUND = 'NO_HH_FOUND'

# Parameters common across HIT Types
HIT_KEYWORDS = ['data collection', 'listing', 'web search', 'data', 'verify']
HIT_APPROVAL_DELAY = datetime.timedelta(days=2)
MIN_AGREEMENT_PERCENTAGE = 70
MAX_GET_HH_ATTEMPTS = 3
MIN_CONFIRMATIONS = 2

MAX_ASSIGNMENTS_TO_PUBLISH = 9

# Number of times we continue to request data if location is unreachable by phone
PHONE_UNREACHABLE_LIMIT = 3

# Qualifications required of users
MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED = 80
MIN_HITS_COMPLETED = 100

# Files to pull and record data
UPDATED_WEBSITE_DATA_FILE = settings.BASE_DIR + "/vp/mturk/temp/website_data.csv"
NEW_PHONE_DATA_FILE = settings.BASE_DIR + "/vp/mturk/temp/new_phone_data.csv"
UPDATED_PHONE_DATA_FILE = settings.BASE_DIR + "/vp/mturk/temp/phone_data.csv"
WEBSITE_STATS_FILE = settings.BASE_DIR + "/vp/mturk/temp/website_stats.csv"
PHONE_STATS_FILE = settings.BASE_DIR + "/vp/mturk/temp/phone_stats.csv"

WEBSITE_UPDATE_FREQUENCY = 600 # in seconds
PHONE_UPDATE_FREQUENCY = 1800

# HIT Status
REVIEWABLE = 'Reviewable'

# Assignment Status
SUBMITTED = 'Submitted'
REJECTED = 'Rejected'

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

# Enum for stage on MTurk
MTURK_STAGE = {
    VERIFY_WEBSITE: 1,
    FIND_WEBSITE_HH_B: 3,
    CONFIRM_WEBSITE_HH_B: 4,
    FIND_PHONE_HH: 5,
    CONFIRM_PHONE_HH: 6,
    CATEGORIZE: 7,
    COMPLETE: 8,
    NO_HH_FOUND: 9
}