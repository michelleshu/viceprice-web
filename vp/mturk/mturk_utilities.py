__author__ = 'michelleshu'

from boto.mturk import price
from boto.mturk.layoutparam import *
from boto.mturk.qualification import *
import unicodecsv as csv
import os.path
from mturk_location import *
from common_constants import *
from viceprice import settings

'''
mturk_utilities.py
This file contains the main utility functions for adding tasks and retrieving updates on location information from MTurk
'''

#region Constants

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
        LAYOUT_ID: '3247MKAWG4CGGI9FPC20JYMRJ184TL',
        MAX_ASSIGNMENTS: 3,
        PRICE: 0.03, #0.01,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    FIND_WEBSITE_HH_B: {
        TITLE: 'Copy information from a website',
        DESCRIPTION: 'Your goal is to copy happy hours information from a website.',
        ANNOTATION: 'Copy happy hour information from a website',
        LAYOUT_PARAMETER_NAMES: ['name', 'url'],
        LAYOUT_ID: '3TFBXQQ2O9UVMLVFYRL6W725544ABC',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.10, #0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    CONFIRM_WEBSITE_HH_B: {
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
        LAYOUT_ID: '3XFRS2SHGGDVGVO4PHSAOU8T2FF4UC',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.10, #0.05,
        DURATION: 3600,
        US_LOCALE_REQUIRED: False
    },

    FIND_PHONE_HH: {
        TITLE: 'Call a business to find what Happy Hours they have',
        DESCRIPTION: 'Your goal is to call a bar or restaurant and find out what happy hours they have.',
        ANNOTATION: 'Call for happy hour info',
        LAYOUT_PARAMETER_NAMES: ['name', 'phone_number'],
        LAYOUT_ID: '3XAF2SZQT2A3G09XWQVI56R0JUQ7F0',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.40, #0.20,
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
        LAYOUT_ID: '31UQTP6TGX7AP8JLJK4IMMMER8SQRB',
        MAX_ASSIGNMENTS: 1,
        PRICE: 0.40, #0.20,
        DURATION: 7200,
        US_LOCALE_REQUIRED: True
    }
}


#endregion

#region CSV Processing

# Parse CSV data into location objects
def get_location_objects_from_csv(filename):
    location_objects = []

    with open(filename, 'rb') as input_file:
        filereader = csv.reader(input_file, encoding='utf-8')

        headers = next(filereader)

        for row in filereader:
            location = MTurkLocation()

            i = 0
            while i < len(row):
                setattr(location, headers[i], row[i].replace("amp;", "").replace("&#10;", "\r\n").replace("&", "&amp;").replace("\r\n", "&#10;"))
                i = i + 1

            location_objects.append(location)

        input_file.close()

    return location_objects


# Write location objects to a CSV file
def write_location_objects_to_csv(locations, filename, append = False):
    mode = 'wb'
    if append:
        mode = 'ab'

        # Create file with headers if it does not exist
        if not os.path.isfile(filename):
            with open(filename, 'w') as output_file:
                filewriter = csv.writer(output_file, encoding='utf-8')
                filewriter.writerow(LOCATION_PROPERTIES)
                output_file.close()

    with open(filename, mode) as output_file:
        filewriter = csv.writer(output_file, encoding='utf-8')

        if not append:
            filewriter.writerow(LOCATION_PROPERTIES)

        for location in locations:
            row = []
            for property in LOCATION_PROPERTIES:
                if property == 'hit_id':
                    print(getattr(location, property))

                value = getattr(location, property)

                if value is not None and type(value) is str:
                    value = value.encode("utf-8")

                row.append(value)
            filewriter.writerow(row)
            print("Row written: ")
            print(row)

        output_file.close()


def print_csv(filename):
    with open(filename, 'rb') as input_file:
        filereader = csv.reader(input_file, encoding='utf-8')

        headers = next(filereader)

        print("Headers: ")
        print(headers)

        for row in filereader:
            print(row)

        input_file.close()


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


# Read layout parameters from a CSV source file and create corresponding HITs
# To deprecate in future and replace with database read
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
        if parameter_value != None:
            parameter_value = parameter_value.replace("<", "&lt;")
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
        if qa.qid == question_id:
            return qa.fields[0]
    # Return None if not found
    return None


# Check to see if domain names of two URLs match (
def domains_match(a, b):
    # Check for empty string
    if (a == ""):
        return b == ""
    if (b == ""):
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

            location.comments = location.comments + comments

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

            location.comments = location.comments + comments

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

    location.monday_start_time = get_answer(answers, MONDAY_START_TIME)
    location.monday_end_time = get_answer(answers, MONDAY_END_TIME)
    location.monday_description = get_answer(answers, MONDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.tuesday_start_time = get_answer(answers, TUESDAY_START_TIME)
    location.tuesday_end_time = get_answer(answers, TUESDAY_END_TIME)
    location.tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.wednesday_start_time = get_answer(answers, WEDNESDAY_START_TIME)
    location.wednesday_end_time = get_answer(answers, WEDNESDAY_END_TIME)
    location.wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.thursday_start_time = get_answer(answers, THURSDAY_START_TIME)
    location.thursday_end_time = get_answer(answers, THURSDAY_END_TIME)
    location.thursday_description = get_answer(answers, THURSDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.friday_start_time = get_answer(answers, FRIDAY_START_TIME)
    location.friday_end_time = get_answer(answers, FRIDAY_END_TIME)
    location.friday_description = get_answer(answers, FRIDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.saturday_start_time = get_answer(answers, SATURDAY_START_TIME)
    location.saturday_end_time = get_answer(answers, SATURDAY_END_TIME)
    location.saturday_description = get_answer(answers, SATURDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.sunday_start_time = get_answer(answers, SUNDAY_START_TIME)
    location.sunday_end_time = get_answer(answers, SUNDAY_END_TIME)
    location.sunday_description = get_answer(answers, SUNDAY_DESCRIPTION).replace("\r\n", "&#10;")
    location.comments = location.comments + get_answer(answers, COMMENTS)

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
    monday_description = get_answer(answers, MONDAY_DESCRIPTION).replace("\r\n", "&#10;")
    tuesday_start_time = get_answer(answers, TUESDAY_START_TIME)
    tuesday_end_time = get_answer(answers, TUESDAY_END_TIME)
    tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION).replace("\r\n", "&#10;")
    wednesday_start_time = get_answer(answers, WEDNESDAY_START_TIME)
    wednesday_end_time = get_answer(answers, WEDNESDAY_END_TIME)
    wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION).replace("\r\n", "&#10;")
    thursday_start_time = get_answer(answers, THURSDAY_START_TIME)
    thursday_end_time = get_answer(answers, THURSDAY_END_TIME)
    thursday_description = get_answer(answers, THURSDAY_DESCRIPTION).replace("\r\n", "&#10;")
    friday_start_time = get_answer(answers, FRIDAY_START_TIME)
    friday_end_time = get_answer(answers, FRIDAY_END_TIME)
    friday_description = get_answer(answers, FRIDAY_DESCRIPTION).replace("\r\n", "&#10;")
    saturday_start_time = get_answer(answers, SATURDAY_START_TIME)
    saturday_end_time = get_answer(answers, SATURDAY_END_TIME)
    saturday_description = get_answer(answers, SATURDAY_DESCRIPTION).replace("\r\n", "&#10;")
    sunday_start_time = get_answer(answers, SUNDAY_START_TIME)
    sunday_end_time = get_answer(answers, SUNDAY_END_TIME)
    sunday_description = get_answer(answers, SUNDAY_DESCRIPTION).replace("\r\n", "&#10;")
    comments = get_answer(answers, COMMENTS)

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

    location.comments = location.comments + comments

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

def get_all_updated_locations():
    dt = datetime.datetime.now()
    backup_file_name = settings.BASE_DIR + "/vp/mturk/backups/" + str(dt).replace(" ", "-") + ".csv"

    updated_locations = []
    website_locations_in_progress = []
    phone_locations_in_progress = []

    website_locations = []
    if os.path.isfile(UPDATED_WEBSITE_DATA_FILE):
        website_locations = get_location_objects_from_csv(UPDATED_WEBSITE_DATA_FILE)

    phone_locations = []
    if os.path.isfile(UPDATED_PHONE_DATA_FILE):
        phone_locations = get_location_objects_from_csv(UPDATED_PHONE_DATA_FILE)

    for location in website_locations:
        if int(location.stage) == MTURK_STAGE[COMPLETE]:
            updated_locations.append((location, 'web'))
        elif int(location.stage) == MTURK_STAGE[NO_HH_FOUND]:
            updated_locations.append((location, 'not_found'))
        else:
            website_locations_in_progress.append(location)

    for location in phone_locations:
        if int(location.stage) == MTURK_STAGE[COMPLETE]:
            updated_locations.append((location, 'phone'))
        elif int(location.stage) == MTURK_STAGE[NO_HH_FOUND]:
            updated_locations.append((location, 'not_found'))
        else:
            phone_locations_in_progress.append(location)

    write_location_objects_to_csv(website_locations_in_progress, UPDATED_WEBSITE_DATA_FILE)
    write_location_objects_to_csv(phone_locations_in_progress, UPDATED_PHONE_DATA_FILE)

    if len(updated_locations) > 0:
        write_location_objects_to_csv(updated_locations, backup_file_name)

    return updated_locations