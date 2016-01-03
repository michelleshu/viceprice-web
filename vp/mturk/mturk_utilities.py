__author__ = 'michelleshu'

from boto.mturk import price
from boto.mturk.layoutparam import *
from boto.mturk.qualification import *
import datetime
from django.db.models import Q
from django.utils import timezone
from vp.models import Location, MTurkLocationInfo
from viceprice import settings

'''
mturk_utilities.py
This file contains the main utility functions for adding tasks and retrieving updates on location information from MTurk
'''

#region Constants

# Maximum number of locations to update at any given time
MAX_LOCATIONS_TO_UPDATE = 20

# Days it takes for data to expire
EXPIRATION_PERIOD = 30

# Connection constants
ACCESS_ID = 'AKIAJDPZ5R3VHIQ6LXYA'
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
FIND_WEBSITE_HH = 'FIND_WEBSITE_HH'
CONFIRM_WEBSITE_HH = 'CONFIRM_WEBSITE_HH'
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
MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED = 70
MIN_HITS_COMPLETED = 100

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
    FIND_WEBSITE_HH: 2,
    CONFIRM_WEBSITE_HH: 3,
    FIND_PHONE_HH: 4,
    CONFIRM_PHONE_HH: 5,
    CATEGORIZE: 6,
    COMPLETE: 7,
    NO_HH_FOUND: 8
}

# Data Sources
WEBSITE = 'WEBSITE'
PHONE = 'PHONE'

DATA_SOURCE = {
    WEBSITE: 1,
    PHONE: 2
}

LOCATION_PROPERTIES = [
    "foursquare_id",
    "name",
    "address",
    "url",
    "phone_number",
    "rating",
    "url_provided",
    "url_provided_verified",
    "url_found",
    "get_hh_attempts",
    "deals_confirmations",
    "stage",
    "hit_id",
    "update_started",
    "update_completed",
    "update_cost",
    "monday_start_time",
    "monday_end_time",
    "monday_description",
    "tuesday_start_time",
    "tuesday_end_time",
    "tuesday_description",
    "wednesday_start_time",
    "wednesday_end_time",
    "wednesday_description",
    "thursday_start_time",
    "thursday_end_time",
    "thursday_description",
    "friday_start_time",
    "friday_end_time",
    "friday_description",
    "saturday_start_time",
    "saturday_end_time",
    "saturday_description",
    "sunday_start_time",
    "sunday_end_time",
    "sunday_description",
    "comments"
]

# HIT Answer Parameters
COMMENTS = "comments"
CONFIRM_URL = "confirm-url"
CONFIRMED_RESPONSE = "confirmed"
FIND_URL = "find-url"
FIND_URL_WEBSITE_FIELD = "find-url-websitefield"
BIGGEST_OBJECT = "biggest-object"
FIND_DEALS_URL = "find-deals-url"
DEALS_URL_WEBSITE_FIELD = "deals-url-websitefield"
MONDAY_START_TIME = "monday-start-time"
MONDAY_END_TIME = "monday-end-time"
MONDAY_DESCRIPTION = "monday-description"
TUESDAY_START_TIME = "tuesday-start-time"
TUESDAY_END_TIME = "tuesday-end-time"
TUESDAY_DESCRIPTION = "tuesday-description"
WEDNESDAY_START_TIME = "wednesday-start-time"
WEDNESDAY_END_TIME = "wednesday-end-time"
WEDNESDAY_DESCRIPTION = "wednesday-description"
THURSDAY_START_TIME = "thursday-start-time"
THURSDAY_END_TIME = "thursday-end-time"
THURSDAY_DESCRIPTION = "thursday-description"
FRIDAY_START_TIME = "friday-start-time"
FRIDAY_END_TIME = "friday-end-time"
FRIDAY_DESCRIPTION = "friday-description"
SATURDAY_START_TIME = "saturday-start-time"
SATURDAY_END_TIME = "saturday-end-time"
SATURDAY_DESCRIPTION = "saturday-description"
SUNDAY_START_TIME = "sunday-start-time"
SUNDAY_END_TIME = "sunday-end-time"
SUNDAY_DESCRIPTION = "sunday-description"
WAS_REACHABLE = "was-reachable"
COMMENTS = "comments"

# HIT Type definitions
HIT_TYPES = {
    VERIFY_WEBSITE: {
        TITLE: 'Find/confirm website for a business',
        DESCRIPTION: 'Your goal is to find or confirm a website for a business. You will be given the name, address, and URL.',
        ANNOTATION: 'Find or verify website',
        LAYOUT_PARAMETER_NAMES: ['name', 'address', 'url_provided'],
        LAYOUT_ID: '3HZSWS2KF8728Z8M1YK5R0A49UF2GR',
        MAX_ASSIGNMENTS: 3,
        PRICE: 0.03,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    FIND_WEBSITE_HH: {
        TITLE: 'Copy information from a website',
        DESCRIPTION: 'Your goal is to copy happy hours information from a website.',
        ANNOTATION: 'Copy happy hour information from a website',
        LAYOUT_PARAMETER_NAMES: ['name', 'url'],
        LAYOUT_ID: '3TJZUC06GDLW1YBSZNFIB5IF6FWOLM',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    CONFIRM_WEBSITE_HH: {
        TITLE: 'Confirm information from a website',
        DESCRIPTION: 'Your goal is to verify that information we have matches what is shown on a website.',
        ANNOTATION: 'Confirm happy hour information from Website',
        LAYOUT_PARAMETER_NAMES: [
            'url',
            'friday_description',
            'friday_end_time',
            'friday_start_time',
            'monday_description',
            'monday_end_time',
            'monday_start_time',
            'name',
            'saturday_description',
            'saturday_end_time',
            'saturday_start_time',
            'sunday_description',
            'sunday_end_time',
            'sunday_start_time',
            'thursday_description',
            'thursday_end_time',
            'thursday_start_time',
            'tuesday_description',
            'tuesday_end_time',
            'tuesday_start_time',
            'wednesday_description',
            'wednesday_end_time',
            'wednesday_start_time'
        ],
        LAYOUT_ID: '3HMQ92ECHMPD8JTLM7ZK1NIIFZOG9U',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    FIND_PHONE_HH: {
        TITLE: 'Call a business to find what Happy Hours they have',
        DESCRIPTION: 'Your goal is to call a bar or restaurant and find out what happy hours they have.',
        ANNOTATION: 'Call for happy hour info',
        LAYOUT_PARAMETER_NAMES: ['name', 'phone_number'],
        LAYOUT_ID: '3773MO9C6K1J30KC6GNVDFYIWBOZRP',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.25,
        DURATION: 7200,
        US_LOCALE_REQUIRED: True
    },

    CONFIRM_PHONE_HH: {
        TITLE: 'Confirm/update our information by calling a business',
        DESCRIPTION: 'Your goal is to call a bar or restaurant and confirm/update our happy hour information',
        ANNOTATION: 'Call to confirm happy hour info',
        LAYOUT_PARAMETER_NAMES: [
            'name',
            'phone_number',
            'friday_description',
            'friday_end_time',
            'friday_start_time',
            'monday_description',
            'monday_end_time',
            'monday_start_time',
            'saturday_description',
            'saturday_end_time',
            'saturday_start_time',
            'sunday_description',
            'sunday_end_time',
            'sunday_start_time',
            'thursday_description',
            'thursday_end_time',
            'thursday_start_time',
            'tuesday_description',
            'tuesday_end_time',
            'tuesday_start_time',
            'wednesday_description',
            'wednesday_end_time',
            'wednesday_start_time'
        ],
        LAYOUT_ID: '3Q91EFBMZH25X1K39E120B6G21PDLE',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.25,
        DURATION: 7200,
        US_LOCALE_REQUIRED: True
    }
}


#endregion


#region Read/write MTurkLocationInfo

# Add locations to update process that need to be updated
def add_mturk_locations_to_update(conn):

    currently_updating = MTurkLocationInfo.objects.filter(~Q(id = MTURK_STAGE[NO_HH_FOUND])).count() # number of updates in progress
    max_new_locations = MAX_LOCATIONS_TO_UPDATE - currently_updating

    # Get at most max_new_locations locations that have either just been added or expired
    earliest_unexpired_date = timezone.now() - datetime.timedelta(days=EXPIRATION_PERIOD)
    new_foursquare_locations = Location.objects.filter(
        Q(mturkLastUpdateCompleted__isnull=True) & Q(rating__gt=9.0)
    )
    # new_foursquare_locations = Location.objects.filter(
    #         Q(mturkLastUpdateCompleted__isnull=True) | Q(mturkLastUpdateCompleted__lt=earliest_unexpired_date)
    #     )[0:max_new_locations]

    # Add new Foursquare locations to MTurkLocationInfo
    for location in new_foursquare_locations:

        # Create a new location info object
        mturk_location = MTurkLocationInfo(
            foursquare_id = location.foursquareId,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            rating = location.rating,
            url_provided = location.website,
            get_hh_attempts = 0,
            deals_confirmations = 0,
            stage = 1,
            update_started = timezone.now(),
            update_cost = 0.0
        )

        # Initialize first HIT for new location
        create_hit(conn, mturk_location, HIT_TYPES[VERIFY_WEBSITE])

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.mturkLastUpdateCompleted = timezone.now()
        location.save()

        mturk_location.save()


# Retrieve in progress website updates
def get_website_update_locations():

    website_stages = [
        MTURK_STAGE[VERIFY_WEBSITE],
        MTURK_STAGE[FIND_WEBSITE_HH],
        MTURK_STAGE[CONFIRM_WEBSITE_HH]
    ];

    return MTurkLocationInfo.objects.filter(stage__in=website_stages)


# Retrieve in progress phone updates
def get_phone_update_locations():

    phone_stages = [
        MTURK_STAGE[FIND_PHONE_HH],
        MTURK_STAGE[CONFIRM_PHONE_HH]
    ];

    return MTurkLocationInfo.objects.filter(stage__in=phone_stages)


# Retrieve completed locations
def get_complete_locations():
    return MTurkLocationInfo.objects.filter(stage=MTURK_STAGE[COMPLETE])


# Retrieve info not found locations
def get_info_not_found_locations():
    return MTurkLocationInfo.objects.filter(stage=MTURK_STAGE[NO_HH_FOUND])

#endregion

#region HIT Creation and Updates

# Register HIT Types with Mechanical Turk and save off HIT type IDs
def register_hit_types(conn):

    for hit_type_name in HIT_TYPES:
        hit_type = HIT_TYPES[hit_type_name]

        min_percentage_qualification = PercentAssignmentsApprovedRequirement(
            "GreaterThan", MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED, required_to_preview=True)
        min_hits_completed_qualification = NumberHitsApprovedRequirement(
            "GreaterThan", MIN_HITS_COMPLETED, required_to_preview=True)
        us_locale_qualification = LocaleRequirement(
            "EqualTo", "US", required_to_preview=True)

        qualifications = Qualifications()
        qualifications.add(min_percentage_qualification)
        qualifications.add(min_hits_completed_qualification)
        if hit_type[US_LOCALE_REQUIRED]:
            qualifications.add(us_locale_qualification)

        hit_type[HIT_TYPE_ID] = conn.register_hit_type(
            hit_type[TITLE],
            hit_type[DESCRIPTION],
            hit_type[PRICE],
            hit_type[DURATION],
            HIT_KEYWORDS,
            approval_delay=None,
            qual_req=qualifications)[0].HITTypeId


# Read layout parameters from MTurkLocationInfo object and create a HIT
def create_hit(conn, location, hit_type):

    # Use qualifications: MIN_PERCENTAGE_APPROVED, MIN_HITS_COMPLETED and optionally US_LOCALE_REQUIRED
    min_percentage_qualification = PercentAssignmentsApprovedRequirement(
        "GreaterThan", MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED, required_to_preview=True)
    min_hits_completed_qualification = NumberHitsApprovedRequirement(
        "GreaterThan", MIN_HITS_COMPLETED, required_to_preview=True)
    us_locale_qualification = LocaleRequirement(
        "EqualTo", "US", required_to_preview=True)

    qualifications = Qualifications()
    qualifications.add(min_percentage_qualification)
    qualifications.add(min_hits_completed_qualification)
    if hit_type[US_LOCALE_REQUIRED]:
        qualifications.add(us_locale_qualification)

    layout_parameter_names = hit_type[LAYOUT_PARAMETER_NAMES]

    layout_parameters = []
    for parameter_name in layout_parameter_names:
        parameter_value = getattr(location, parameter_name)
        if parameter_value != None and isinstance(parameter_value, str):
            parameter_value = parameter_value.replace("<", "&lt;").replace("&", "and")

        if parameter_name[-4:] == 'time' and parameter_value != None:
            parameter_value = parameter_value.strftime("%H:%M")

        layout_parameters.append(LayoutParameter(parameter_name, parameter_value))

    hit = conn.create_hit(
        hit_type=hit_type[HIT_TYPE_ID],
        question=None,
        hit_layout=hit_type[LAYOUT_ID],
        lifetime=datetime.timedelta(days=7),
        max_assignments=hit_type[MAX_ASSIGNMENTS],
        title=hit_type[TITLE],
        description=hit_type[DESCRIPTION],
        keywords=HIT_KEYWORDS,
        reward=price.Price(amount=hit_type[PRICE], currency_code='USD'),
        duration=hit_type[DURATION],
        approval_delay=HIT_APPROVAL_DELAY,
        annotation=hit_type[ANNOTATION],
        questions=None,
        layout_params=LayoutParameters(layout_parameters),
        response_groups = None,
        qualifications = qualifications
    )

    location.hit_id = hit[0].HITId
    location.update_cost = location.update_cost + hit_type[PRICE]


# Retrieve answer field value in list of QuestionFormAnswers for HIT to the question with matching questionId tag
def get_answer(answers, question_id):
    for qa in answers:
        if qa.qid == question_id and qa.fields[0] != '' and qa.fields[0] != 'None':
            return qa.fields[0]
    # Return None if not found
    return None


# Check to see if domain names of two URLs match (
def domains_match(a, b):
    # Check for empty string
    if (a == "" or a == None):
        return b == "" or b == None
    if (b == "" or b == None):
        return False

    # Strip backslash from end if it exists
    if (a[-1] == '/'):
        a = a[:-1]

    if (b[-1] == '/'):
        b = b[:-1]

    # Get tail that comes after optional http and www
    a = a.replace("https://", "").replace("http://", "")
    b = b.replace("https://", "").replace("http://", "")
    a_start_index = a.find("www.")
    if (a_start_index == -1):
        a_start_index = 0
    else:
        a_start_index = a_start_index + 4

    b_start_index = b.find("www.")
    if (b_start_index == -1):
        b_start_index = 0
    else:
        b_start_index = b_start_index + 4

    return a[a_start_index:].strip().lower() == b[b_start_index:].strip().lower()


# Get the agreement percentage among a set of URLs and the URL with the highest agreement percentage
def get_url_agreement_percentage(urls):
    i = 0
    max_agreement_percentage = 0
    max_agreed_url = ""
    while (i < len(urls)):
        # For each url in list, compare to all other urls in list not including itself and calculate agreement
        # percentage overall
        agrees = 0
        disagrees = 0
        j = 0
        while(j < len(urls)):
            if (i != j):
                if (domains_match(urls[i], urls[j])):
                    agrees = agrees + 1
                else:
                    disagrees = disagrees + 1
            j = j + 1

        # Add one here to numerator and denominator to count the url itself in the agreement percentage
        # For instance, if we have two submissions that are the same and one that is different, the percentage
        # should be 66.7
        agreement_percentage = (agrees + 1.0) / (agrees + disagrees + 1.0) * 100.0

        # Choose the max of the agreement percentages we have seen relative to the base url used for comparison
        if (agreement_percentage > max_agreement_percentage):
            max_agreement_percentage = agreement_percentage
            max_agreed_url = urls[i]
        i = i + 1

    # Return the maximum agreement percentage seen and the url that corresponds to it
    return (max_agreement_percentage, max_agreed_url)


# Process the assignments from a verify website HIT (Stage 1)
# Return the URL agreement percentage and agreed upon URL
def process_verify_website_hit_assignments(conn, location, assignments):
    hit_id = location.hit_id
    url_responses = []

    for assignment in assignments:
        if assignment.AssignmentStatus != REJECTED:
            answers = assignment.answers[0]
            confirm_url = get_answer(answers, CONFIRM_URL)
            find_url = get_answer(answers, FIND_URL)
            url_found = get_answer(answers, FIND_URL_WEBSITE_FIELD)
            biggest_object = get_answer(answers, BIGGEST_OBJECT)
            comments = get_answer(answers, COMMENTS)

            if (biggest_object != "correct"):
                if assignment.AssignmentStatus == SUBMITTED:
                    conn.reject_assignment(assignment.AssignmentId, "Failed attention check question. The car is the biggest object.")
                conn.extend_hit(hit_id, assignments_increment = 1)
                return None

            if (find_url == "1"):
                if (url_found == None or ''):
                    if assignment.AssignmentStatus == SUBMITTED:
                        conn.reject_assignment(assignment.AssignmentId, 'Found website through web search but did not paste URL as requested in instructions')
                    conn.extend_hit(hit_id, assignments_increment=1)
                    return None

            if (confirm_url == "1"):
                url_responses.append(CONFIRMED_RESPONSE)
            else:
                url_responses.append(url_found)

            if (comments != None and comments != ""):
                if (location.comments == None):
                    location.comments = ""

                location.comments = location.comments + "\n" + comments

    return get_url_agreement_percentage(url_responses)


# Process the assignments from a find happy hour URL HIT (Stage 2)
# Return the happy hour URL agreement percentage and agreed upon URL
def process_find_happy_hour_url_assignments(conn, location, assignments):
    hit_id = location.hit_id
    deals_url_responses = []

    for assignment in assignments:
        if assignment.AssignmentStatus != REJECTED:
            answers = assignment.answers[0]
            find_deals_url = get_answer(answers, FIND_DEALS_URL)
            deals_url = get_answer(answers, DEALS_URL_WEBSITE_FIELD)
            biggest_object = get_answer(answers, BIGGEST_OBJECT)
            comments = get_answer(answers, COMMENTS)

            if biggest_object != "correct":
                if assignment.AssignmentStatus == SUBMITTED:
                    conn.reject_assignment(assignment.AssignmentId, "Failed attention check question. The car is the biggest object.")
                conn.extend_hit(hit_id, assignments_increment = 1)
                return None

            if find_deals_url == "1":
                if deals_url == None or '':
                    if assignment.AssignmentStatus == SUBMITTED:
                        conn.reject_assignment(assignment.AssignmentId, 'Found happy hour URL through web search but did not paste URL as requested in instructions')
                    conn.extend_hit(hit_id, assignments_increment=1)
                    return None

            if (comments != None and comments != ""):
                if (location.comments == None):
                    location.comments = ""

                location.comments = location.comments + "\n" + comments

            deals_url_responses.append(deals_url)

    return get_url_agreement_percentage(deals_url_responses)


# Get whether happy hour was found on website
# If not, update happy hour attempt cound
def was_website_hh_found(conn, location, assignment):
    answers = assignment.answers[0]

    if get_answer(answers, FIND_DEALS_URL) == "1":
        return True
    else:
        location.get_hh_attempts = int(location.get_hh_attempts) + 1
        return False


# Process the assignments from a find website happy hour info HIT (Stage 3)
# Set columns on location object according to happy hour info provided
# Return true on success, false if no happy hours found, None if failed attention check question
def process_find_happy_hour_info_assignment(conn, location, assignment):
    answers = assignment.answers[0]

    if get_answer(answers, BIGGEST_OBJECT) != "correct":
        if assignment.AssignmentStatus == SUBMITTED:
            conn.reject_assignment(assignment.AssignmentId, "Failed attention check question. The car is the biggest object.")
        return None

    monday_start_time = get_answer(answers, MONDAY_START_TIME)
    monday_end_time = get_answer(answers, MONDAY_END_TIME)
    location.monday_description = get_answer(answers, MONDAY_DESCRIPTION)
    tuesday_start_time = get_answer(answers, TUESDAY_START_TIME)
    tuesday_end_time = get_answer(answers, TUESDAY_END_TIME)
    location.tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION)
    wednesday_start_time = get_answer(answers, WEDNESDAY_START_TIME)
    wednesday_end_time = get_answer(answers, WEDNESDAY_END_TIME)
    location.wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION)
    thursday_start_time = get_answer(answers, THURSDAY_START_TIME)
    thursday_end_time = get_answer(answers, THURSDAY_END_TIME)
    location.thursday_description = get_answer(answers, THURSDAY_DESCRIPTION)
    friday_start_time = get_answer(answers, FRIDAY_START_TIME)
    friday_end_time = get_answer(answers, FRIDAY_END_TIME)
    location.friday_description = get_answer(answers, FRIDAY_DESCRIPTION)
    saturday_start_time = get_answer(answers, SATURDAY_START_TIME)
    saturday_end_time = get_answer(answers, SATURDAY_END_TIME)
    location.saturday_description = get_answer(answers, SATURDAY_DESCRIPTION)
    sunday_start_time = get_answer(answers, SUNDAY_START_TIME)
    sunday_end_time = get_answer(answers, SUNDAY_END_TIME)
    location.sunday_description = get_answer(answers, SUNDAY_DESCRIPTION)

    # Convert strings to times
    if (monday_start_time != None and monday_start_time != ''):
        monday_start_time = datetime.datetime.strptime(monday_start_time, "%H:%M").time()
    if (tuesday_start_time != None and tuesday_start_time != ''):
        tuesday_start_time  = datetime.datetime.strptime(tuesday_start_time, "%H:%M").time()
    if (wednesday_start_time != None and wednesday_start_time != ''):
        wednesday_start_time = datetime.datetime.strptime(wednesday_start_time, "%H:%M").time()
    if (thursday_start_time != None and thursday_start_time != ''):
        thursday_start_time = datetime.datetime.strptime(thursday_start_time, "%H:%M").time()
    if (friday_start_time != None and friday_start_time != ''):
        friday_start_time = datetime.datetime.strptime(friday_start_time, "%H:%M").time()
    if (saturday_start_time != None and saturday_start_time != ''):
        saturday_start_time = datetime.datetime.strptime(saturday_start_time, "%H:%M").time()
    if (sunday_start_time != None and sunday_start_time != ''):
        sunday_start_time = datetime.datetime.strptime(sunday_start_time, "%H:%M").time()

    if (monday_end_time != None and monday_end_time != ''):
        monday_end_time = datetime.datetime.strptime(monday_end_time, "%H:%M").time()
    print(tuesday_end_time)
    if (tuesday_end_time != None and tuesday_end_time != ''):
        tuesday_end_time = datetime.datetime.strptime(tuesday_end_time, "%H:%M").time()
    if (wednesday_end_time != None and wednesday_end_time != ''):
        wednesday_end_time = datetime.datetime.strptime(wednesday_end_time, "%H:%M").time()
    if (thursday_end_time != None and thursday_end_time != ''):
        thursday_end_time = datetime.datetime.strptime(thursday_end_time, "%H:%M").time()
    if (friday_end_time != None and friday_end_time != ''):
        friday_end_time = datetime.datetime.strptime(friday_end_time, "%H:%M").time()
    if (saturday_end_time != None and saturday_end_time != ''):
        saturday_end_time = datetime.datetime.strptime(saturday_end_time, "%H:%M").time()
    if (sunday_end_time != None and sunday_end_time != ''):
        sunday_end_time = datetime.datetime.strptime(sunday_end_time, "%H:%M").time()

    location.monday_start_time = monday_start_time
    location.tuesday_start_time = tuesday_start_time
    location.wednesday_start_time = wednesday_start_time
    location.thursday_start_time = thursday_start_time
    location.friday_start_time = friday_start_time
    location.saturday_start_time = saturday_start_time
    location.sunday_start_time = sunday_start_time

    location.monday_end_time = monday_end_time
    location.tuesday_end_time = tuesday_end_time
    location.wednesday_end_time = wednesday_end_time
    location.thursday_end_time = thursday_end_time
    location.friday_end_time = friday_end_time
    location.saturday_end_time = saturday_end_time
    location.sunday_end_time = sunday_end_time

    if get_answer(answers, COMMENTS) != None:
        if location.comments == None:
            location.comments = ""
        location.comments = location.comments + "\n" + get_answer(answers, COMMENTS)

    return True


# Process the assignments from a confirm website happy hour info HIT (Stage 4)
# Set columns on location object according to happy hour info provided
# Set confirmation count on location to number of confirmations received
# Return confirmation or None if failed attention check
def process_confirm_happy_hour_info_assignment(conn, location, assignment):
    confirmed = True
    answers = assignment.answers[0]

    if get_answer(answers, BIGGEST_OBJECT) != "correct":
        if assignment.AssignmentStatus == SUBMITTED:
            conn.reject_assignment(assignment.AssignmentId, "Failed attention check question. The car is the biggest object.")
        return None

    monday_start_time = get_answer(answers, MONDAY_START_TIME)
    monday_end_time = get_answer(answers, MONDAY_END_TIME)
    monday_description = get_answer(answers, MONDAY_DESCRIPTION)
    tuesday_start_time = get_answer(answers, TUESDAY_START_TIME)
    tuesday_end_time = get_answer(answers, TUESDAY_END_TIME)
    tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION)
    wednesday_start_time = get_answer(answers, WEDNESDAY_START_TIME)
    wednesday_end_time = get_answer(answers, WEDNESDAY_END_TIME)
    wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION)
    thursday_start_time = get_answer(answers, THURSDAY_START_TIME)
    thursday_end_time = get_answer(answers, THURSDAY_END_TIME)
    thursday_description = get_answer(answers, THURSDAY_DESCRIPTION)
    friday_start_time = get_answer(answers, FRIDAY_START_TIME)
    friday_end_time = get_answer(answers, FRIDAY_END_TIME)
    friday_description = get_answer(answers, FRIDAY_DESCRIPTION)
    saturday_start_time = get_answer(answers, SATURDAY_START_TIME)
    saturday_end_time = get_answer(answers, SATURDAY_END_TIME)
    saturday_description = get_answer(answers, SATURDAY_DESCRIPTION)
    sunday_start_time = get_answer(answers, SUNDAY_START_TIME)
    sunday_end_time = get_answer(answers, SUNDAY_END_TIME)
    sunday_description = get_answer(answers, SUNDAY_DESCRIPTION)
    comments = get_answer(answers, COMMENTS)

    # Convert strings to times
    if (monday_start_time != None and monday_start_time != ''):
        monday_start_time = datetime.datetime.strptime(monday_start_time, "%H:%M").time()
    if (tuesday_start_time != None and tuesday_start_time != ''):
        tuesday_start_time  = datetime.datetime.strptime(tuesday_start_time, "%H:%M").time()
    if (wednesday_start_time != None and wednesday_start_time != ''):
        wednesday_start_time = datetime.datetime.strptime(wednesday_start_time, "%H:%M").time()
    if (thursday_start_time != None and thursday_start_time != ''):
        thursday_start_time = datetime.datetime.strptime(thursday_start_time, "%H:%M").time()
    if (friday_start_time != None and friday_start_time != ''):
        friday_start_time = datetime.datetime.strptime(friday_start_time, "%H:%M").time()
    if (saturday_start_time != None and saturday_start_time != ''):
        saturday_start_time = datetime.datetime.strptime(saturday_start_time, "%H:%M").time()
    if (sunday_start_time != None and sunday_start_time != ''):
        sunday_start_time = datetime.datetime.strptime(sunday_start_time, "%H:%M").time()

    if (monday_end_time != None and monday_end_time != ''):
        monday_end_time = datetime.datetime.strptime(monday_end_time, "%H:%M").time()
    if (tuesday_end_time != None and tuesday_end_time != ''):
        tuesday_end_time = datetime.datetime.strptime(tuesday_end_time, "%H:%M").time()
    if (wednesday_end_time != None and wednesday_end_time != ''):
        wednesday_end_time = datetime.datetime.strptime(wednesday_end_time, "%H:%M").time()
    if (thursday_end_time != None and thursday_end_time != ''):
        thursday_end_time = datetime.datetime.strptime(thursday_end_time, "%H:%M").time()
    if (friday_end_time != None and friday_end_time != ''):
        friday_end_time = datetime.datetime.strptime(friday_end_time, "%H:%M").time()
    if (saturday_end_time != None and saturday_end_time != ''):
        saturday_end_time = datetime.datetime.strptime(saturday_end_time, "%H:%M").time()
    if (sunday_end_time != None and sunday_end_time != ''):
        sunday_end_time = datetime.datetime.strptime(sunday_end_time, "%H:%M").time()


    if (location.monday_start_time != monday_start_time):
        confirmed = False
        location.monday_start_time = monday_start_time
    if (location.monday_end_time != monday_end_time):
        confirmed = False
        location.monday_end_time = monday_end_time
    if (location.monday_description != monday_description):
        confirmed = False
        location.monday_description = monday_description

    if (location.tuesday_start_time != tuesday_start_time):
        confirmed = False
        location.tuesday_start_time = tuesday_start_time
    if (location.tuesday_end_time != tuesday_end_time):
        confirmed = False
        location.tuesday_end_time = tuesday_end_time
    if (location.tuesday_description != tuesday_description):
        confirmed = False
        location.tuesday_description = tuesday_description

    if (location.wednesday_start_time != wednesday_start_time):
        confirmed = False
        location.wednesday_start_time = wednesday_start_time
    if (location.wednesday_end_time != wednesday_end_time):
        confirmed = False
        location.wednesday_end_time = wednesday_end_time
    if (location.wednesday_description != wednesday_description):
        confirmed = False
        location.wednesday_description = wednesday_description

    if (location.thursday_start_time != thursday_start_time):
        confirmed = False
        location.thursday_start_time = thursday_start_time
    if (location.thursday_end_time != thursday_end_time):
        confirmed = False
        location.thursday_end_time = thursday_end_time
    if (location.thursday_description != thursday_description):
        confirmed = False
        location.thursday_description = thursday_description

    if (location.friday_start_time != friday_start_time):
        confirmed = False
        location.friday_start_time = friday_start_time
    if (location.friday_end_time != friday_end_time):
        confirmed = False
        location.friday_end_time = friday_end_time
    if (location.friday_description != friday_description):
        confirmed = False
        location.friday_description = friday_description

    if (location.saturday_start_time != saturday_start_time):
        confirmed = False
        location.saturday_start_time = saturday_start_time
    if (location.saturday_end_time != saturday_end_time):
        confirmed = False
        location.saturday_end_time = saturday_end_time
    if (location.saturday_description != saturday_description):
        confirmed = False
        location.saturday_description = saturday_description

    if (location.sunday_start_time != sunday_start_time):
        confirmed = False
        location.sunday_start_time = sunday_start_time
    if (location.sunday_end_time != sunday_end_time):
        confirmed = False
        location.sunday_end_time = sunday_end_time
    if (location.sunday_description != sunday_description):
        confirmed = False
        location.sunday_description = sunday_description

    if (confirmed):
        location.deals_confirmations = int(location.deals_confirmations) + 1
    else:
        location.deals_confirmations = 0

    if (comments != None and comments != ""):
        if (location.comments == None):
            location.comments = ""

        location.comments = location.comments + "\n" + comments

    return confirmed

# Process the assignments from a find website happy hour info by phone HIT (Stage 5)
# Set columns on location object according to happy hour info provided
# Return true if happy hour information found or if HIT was continued
# Return false if wrong phone number
def process_find_happy_hour_info_assignment_phone(conn, location, assignment):
    answers = assignment.answers[0]
    was_reachable = get_answer(answers, WAS_REACHABLE)

    # Reachable by phone and happy hour info found
    if was_reachable == "1":
        processed = process_find_happy_hour_info_assignment(conn, location, assignment)

        if (processed == None):
            # Failed attention check
            return None

        location.stage = MTURK_STAGE[CONFIRM_PHONE_HH]
        return True
    # Not reachable by phone
    elif was_reachable == "2":
        conn.extend_hit(location.hit_id, assignments_increment=1)
        return True
    # Wrong phone number
    elif was_reachable == "3":
        return False


# Extend the hit if not reachable by phone or if failed attention check
# Return True if extended
def extend_if_not_reachable(conn, location, assignments):
    answers = assignments[-1].answers[0]
    was_reachable = get_answer(answers, WAS_REACHABLE)
    biggest_object = get_answer(answers, BIGGEST_OBJECT)

    if biggest_object != "correct":
        if assignments[-1].AssignmentStatus == SUBMITTED:
            conn.reject_assignment(assignments[-1].AssignmentId, "Failed attention check question. The car is the biggest object.")
        conn.extend_hit(location.hit_id, assignments_increment=1)
        return True

    if was_reachable == "2":
        if len(assignments) >= PHONE_UNREACHABLE_LIMIT:
            location.comments = "Unreachable by phone"
            location.stage = MTURK_STAGE[NO_HH_FOUND]

        else:
            conn.extend_hit(location.hit_id, assignments_increment=1)

        return True

    return False


# Approve assignments from HIT and dispose of the HIT
def approve_and_dispose(conn, hit):
    if (hit.HITStatus == REVIEWABLE):
        for assignment in conn.get_assignments(hit.HITId):
            if (assignment.AssignmentStatus == SUBMITTED):
                conn.approve_assignment(assignment.AssignmentId)

        conn.dispose_hit(hit.HITId)

#endregion
