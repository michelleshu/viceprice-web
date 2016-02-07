__author__ = 'michelleshu'

from boto.mturk import price
from boto.mturk.layoutparam import *
from boto.mturk.qualification import *
import datetime
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from pprint import pprint
from vp.models import Location, MTurkLocationInfo, DayOfWeek, TimeFrame
from viceprice.constants import *

'''
mturk_utilities.py
This file contains the main utility functions for adding tasks and retrieving updates on location information from MTurk
'''


#region Get locations for update

# Add locations to update process that need to be updated
def add_mturk_locations_to_update(conn, max_to_add = None):
    if (max_to_add == None):
        max_to_add = MAX_LOCATIONS_TO_UPDATE

    currently_updating = MTurkLocationInfo.objects.filter(
        ~Q(stage = MTURK_STAGE[NO_INFO]) & ~Q(stage = MTURK_STAGE[COMPLETE])).count() # number of updates in progress
    max_new_locations = max_to_add - currently_updating

    # Get at most max_new_locations locations that have either just been added or expired
    earliest_unexpired_date = timezone.now() - datetime.timedelta(days=EXPIRATION_PERIOD)
    new_locations = Location.objects.filter(
        mturkLastUpdateCompleted__lt=earliest_unexpired_date)[0:max_new_locations]

    # Add new Foursquare locations to MTurkLocationInfo
    for location in new_locations:

        # If location has no website, start in Stage 0. Otherwise, start in Stage 1.
        if (location.website == None or location.website == ''):
            stage = MTURK_STAGE[FIND_WEBSITE]
        else:
            stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]

        mturk_location = MTurkLocationInfo(
            location = location,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            website = location.website,
            stage = stage,
            update_started = timezone.now(),
            update_cost = 0.0
        )

        # TODO EDIT this to reflect proper stage when HIT Layout for Stage 1 is made
        # Initialize first HIT for new location
        create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.mturkLastUpdateCompleted = timezone.now()
        location.save()

        mturk_location.save()


# Retrieve in progress website updates
def get_website_update_mturk_locations():

    website_stages = [
        MTURK_STAGE[FIND_WEBSITE],
        MTURK_STAGE[FIND_HAPPY_HOUR_WEB],
        MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
    ]

    return list(MTurkLocationInfo.objects.filter(stage__in=website_stages))


# Retrieve in progress phone updates
def get_phone_update_mturk_locations():

    phone_stages = [
        MTURK_STAGE[FIND_HAPPY_HOUR_PHONE],
        MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]
    ]

    return list(MTurkLocationInfo.objects.filter(stage__in=phone_stages))


# Retrieve completed locations
def get_complete_mturk_locations():
    return MTurkLocationInfo.objects.filter(stage=MTURK_STAGE[COMPLETE])


# Retrieve info not found locations
def get_no_info_mturk_locations():
    return MTurkLocationInfo.objects.filter(stage=MTURK_STAGE[NO_INFO])

#endregion

#region HIT Creation and Updates

# Register HIT Types with Mechanical Turk and save off HIT type IDs
def register_hit_types(conn):

    for hit_type_name in settings.MTURK_HIT_TYPES:
        hit_type = settings.MTURK_HIT_TYPES[hit_type_name]

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
            hit_type[KEYWORDS],
            approval_delay=None,
            qual_req=qualifications)[0].HITTypeId


# Read layout parameters from MTurkLocationInfo object and create a HIT
def create_hit(conn, mturk_location_info, hit_type):

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
        parameter_value = getattr(mturk_location_info, parameter_name)
        if parameter_value != None and isinstance(parameter_value, str):
            # Handle string replacements so names play well with MTurk
            parameter_value = parameter_value.replace("<", "&lt;").replace("&", "and")

        layout_parameters.append(LayoutParameter(parameter_name, parameter_value))

    hit = conn.create_hit(
        hit_type=hit_type[HIT_TYPE_ID],
        question=None,
        hit_layout=hit_type[LAYOUT_ID],
        lifetime=datetime.timedelta(days=7),
        max_assignments=hit_type[MAX_ASSIGNMENTS],
        title=hit_type[TITLE],
        description=hit_type[DESCRIPTION],
        keywords=hit_type[KEYWORDS],
        reward=price.Price(amount=hit_type[PRICE], currency_code='USD'),
        duration=hit_type[DURATION],
        annotation=hit_type[ANNOTATION],
        layout_params=LayoutParameters(layout_parameters),
        qualifications = qualifications
    )

    mturk_location_info.hit_id = hit[0].HITId
    mturk_location_info.update_cost = mturk_location_info.update_cost + hit_type[PRICE]
    mturk_location_info.save()


# Retrieve answer field value in list of QuestionFormAnswers for HIT to the question with matching questionId tag
def get_answer(answers, question_id):
    for qa in answers:
        if qa.qid == question_id and qa.fields[0] != '' and qa.fields[0] != 'None':
            return qa.fields[0]
    # Return None if not found
    return None


# Add comments to MTurkLocationInfo
def add_comments(mturk_location, comments):
    if (comments != None and comments != ''):
        if (mturk_location.comments == None or mturk_location.comments == ''):
            mturk_location.comments = comments
        else:
            mturk_location.comments = mturk_location.comments + '\n' + comments

        mturk_location.comments = mturk_location.comments[:999]
        mturk_location.save()


# Get the agreement percentage among a set of URLs and the URL with the highest agreement percentage
def get_url_agreement_percentage(urls):
    domains = []
    max_agreement_count = 0
    max_agreed_url = ""

    for url in urls:
        if (url == 'None' or url == ''):
            domains.append('')

        else:
            # Remove whitespace and uppercase characters
            url = url.strip().lower()

            # Strip backslash from end if it exists
            if (url[-1] == '/'):
                url = url[:-1]

            # Add domain after optional http://, https://, www to domains
            domains.append(url.lstrip("https://www."))

    # For each domain in list, compare to all other domains and calculate number that agree
    for domain in domains:
        agreement_count = domains.count(domain)
        if (agreement_count > max_agreement_count):
            max_agreement_count = agreement_count
            if (domain == ''):
                max_agreed_url = None
            else:
                max_agreed_url = "http://www." + domain

            if (max_agreement_count > len(domains) / 2):
                return ((max_agreement_count * 100.0) / len(domains), max_agreed_url)

    # Return the maximum agreement percentage seen and the url that corresponds to it
    return ((max_agreement_count * 100.0) / len(domains), max_agreed_url)


# Process the assignments from a verify website HIT (Stage 1)
# Return the URL agreement percentage and agreed upon URL
def process_find_website_hit_assignments(conn, mturk_location, assignments):
    hit_id = mturk_location.hit_id
    url_responses = []

    for assignment in assignments:

        if assignment.AssignmentStatus != REJECTED:
            answers = assignment.answers[0]
            url_found = get_answer(answers, URL_FOUND)
            url = get_answer(answers, URL)
            attention_check = get_answer(answers, ATTENTION_CHECK)
            comments = get_answer(answers, COMMENTS)

            if (attention_check != 'correct'):
                print("Failed attention check")
                if assignment.AssignmentStatus == SUBMITTED:
                    conn.reject_assignment(assignment.AssignmentId, 'Failed attention check question.')
                conn.extend_hit(hit_id, assignments_increment = 1)
                return None

            if (url_found == 'yes'):
                url_responses.append(url)
            else:
                url_responses.append('')

            add_comments(mturk_location, comments)

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

    location.monday_start_time = parse_time(get_answer(answers, MONDAY_START_TIME))
    location.monday_end_time = parse_time(get_answer(answers, MONDAY_END_TIME))
    location.monday_description = get_answer(answers, MONDAY_DESCRIPTION)
    location.tuesday_start_time = parse_time(get_answer(answers, TUESDAY_START_TIME))
    location.tuesday_end_time = parse_time(get_answer(answers, TUESDAY_END_TIME))
    location.tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION)
    location.wednesday_start_time = parse_time(get_answer(answers, WEDNESDAY_START_TIME))
    location.wednesday_end_time = parse_time(get_answer(answers, WEDNESDAY_END_TIME))
    location.wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION)
    location.thursday_start_time = parse_time(get_answer(answers, THURSDAY_START_TIME))
    location.thursday_end_time = parse_time(get_answer(answers, THURSDAY_END_TIME))
    location.thursday_description = get_answer(answers, THURSDAY_DESCRIPTION)
    location.friday_start_time = parse_time(get_answer(answers, FRIDAY_START_TIME))
    location.friday_end_time = parse_time(get_answer(answers, FRIDAY_END_TIME))
    location.friday_description = get_answer(answers, FRIDAY_DESCRIPTION)
    location.saturday_start_time = parse_time(get_answer(answers, SATURDAY_START_TIME))
    location.saturday_end_time = parse_time(get_answer(answers, SATURDAY_END_TIME))
    location.saturday_description = get_answer(answers, SATURDAY_DESCRIPTION)
    location.sunday_start_time = parse_time(get_answer(answers, SUNDAY_START_TIME))
    location.sunday_end_time = parse_time(get_answer(answers, SUNDAY_END_TIME))
    location.sunday_description = get_answer(answers, SUNDAY_DESCRIPTION)

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

    monday_start_time = parse_time(get_answer(answers, MONDAY_START_TIME))
    monday_end_time = parse_time(get_answer(answers, MONDAY_END_TIME))
    monday_description = get_answer(answers, MONDAY_DESCRIPTION)
    tuesday_start_time = parse_time(get_answer(answers, TUESDAY_START_TIME))
    tuesday_end_time = parse_time(get_answer(answers, TUESDAY_END_TIME))
    tuesday_description = get_answer(answers, TUESDAY_DESCRIPTION)
    wednesday_start_time = parse_time(get_answer(answers, WEDNESDAY_START_TIME))
    wednesday_end_time = parse_time(get_answer(answers, WEDNESDAY_END_TIME))
    wednesday_description = get_answer(answers, WEDNESDAY_DESCRIPTION)
    thursday_start_time = parse_time(get_answer(answers, THURSDAY_START_TIME))
    thursday_end_time = parse_time(get_answer(answers, THURSDAY_END_TIME))
    thursday_description = get_answer(answers, THURSDAY_DESCRIPTION)
    friday_start_time = parse_time(get_answer(answers, FRIDAY_START_TIME))
    friday_end_time = parse_time(get_answer(answers, FRIDAY_END_TIME))
    friday_description = get_answer(answers, FRIDAY_DESCRIPTION)
    saturday_start_time = parse_time(get_answer(answers, SATURDAY_START_TIME))
    saturday_end_time = parse_time(get_answer(answers, SATURDAY_END_TIME))
    saturday_description = get_answer(answers, SATURDAY_DESCRIPTION)
    sunday_start_time = parse_time(get_answer(answers, SUNDAY_START_TIME))
    sunday_end_time = parse_time(get_answer(answers, SUNDAY_END_TIME))
    sunday_description = get_answer(answers, SUNDAY_DESCRIPTION)
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

    if (comments != None and comments != ""):
        if (location.comments == None):
            location.comments = comments
        else:
            location.comments = location.comments + "\n" + comments

    return confirmed

# Try to parse a time string. Return None on failure
def parse_time(string):
    if (string == None):
        return None

    # Remove spaces
    string = string.replace(" ", "")
    time = None

    for format in TIME_FORMATS:
        try:
            time = datetime.strptime(string, format).time()
            return time
        except ValueError:
            pass

    return time


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

# Check if a location has happy hour data filled out
def has_happy_hour_data(location):
    has_data = False

    if (location.monday_description != None and location.monday_description != ''):
        if (location.monday_start_time != None and location.monday_end_time != None):
            has_data = True
        else:
            location.monday_description = None
            location.monday_start_time = None
            location.monday_end_time = None

    if (location.tuesday_description != None and location.tuesday_description != ''):
        if (location.tuesday_start_time != None and location.tuesday_end_time != None):
            has_data = True
        else:
            location.tuesday_description = None
            location.tuesday_start_time = None
            location.tuesday_end_time = None

    if (location.wednesday_description != None and location.wednesday_description != ''):
        if (location.wednesday_start_time != None and location.wednesday_end_time != None):
            has_data = True
        else:
            location.wednesday_description = None
            location.wednesday_start_time = None
            location.wednesday_end_time = None

    if (location.thursday_description != None and location.thursday_description != ''):
        if (location.thursday_start_time != None and location.thursday_end_time != None):
            has_data = True
        else:
            location.thursday_description = None
            location.thursday_start_time = None
            location.thursday_end_time = None

    if (location.friday_description != None and location.friday_description != ''):
        if (location.friday_start_time != None and location.friday_end_time != None):
            has_data = True
        else:
            location.friday_description = None
            location.friday_start_time = None
            location.friday_end_time = None

    if (location.saturday_description != None and location.saturday_description != ''):
        if (location.saturday_start_time != None and location.saturday_end_time != None):
            has_data = True
        else:
            location.saturday_description = None
            location.saturday_start_time = None
            location.saturday_end_time = None

    if (location.sunday_description != None and location.sunday_description != ''):
        if (location.sunday_start_time != None and location.sunday_end_time != None):
            has_data = True
        else:
            location.sunday_description = None
            location.sunday_start_time = None
            location.sunday_end_time = None

    return has_data


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

# Check to see whether we are within valid business hours for a location based on Foursquare ID
def within_business_hours(foursquare_id):
    now = timezone.localtime(timezone.now())
    current_day = now.isoweekday()
    current_time = now.time()

    business_hour_ids = Location.objects.get(foursquareId = foursquare_id).businessHours.all().values_list('id', flat=True)
    today_business_hour_ids = DayOfWeek.objects.filter(
        day = current_day, businessHour_id__in=business_hour_ids).values_list('businessHour_id', flat=True)
    today_time_frames = TimeFrame.objects.filter(businessHour_id__in=today_business_hour_ids).all().values('startTime', 'endTime')

    for time_frame in today_time_frames:
        if (within_time_range(current_time, time_frame['startTime'], time_frame['endTime'])):
            return True

    return False



# Check if we are currently within a certain time range
def within_time_range(time, start_time, end_time):
    start_cutoff = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=30)).time()
    end_cutoff = (datetime.datetime.combine(datetime.date.today(), end_time) - datetime.timedelta(minutes=30)).time()

    if (end_cutoff > BUSINESS_HOUR_CUTOFF or end_cutoff < start_cutoff):
        end_cutoff = BUSINESS_HOUR_CUTOFF

    return start_cutoff <= time and end_cutoff >= time