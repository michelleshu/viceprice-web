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

    new_locations = Location.objects.filter(Q(id__gte=2343) & Q(id__lte=2412) & Q(mturkDateLastUpdated__lt=earliest_unexpired_date))[0:max_new_locations]

    # new_locations = Location.objects.filter(
    #     mturkDateLastUpdated__lt=earliest_unexpired_date)[0:max_new_locations]

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
            stage = stage
        )

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.mturkDateLastUpdated = timezone.now()
        location.save()

        mturk_location.save()


# Retrieve in progress website updates
def get_website_update_mturk_locations():

    website_stages = [
        MTURK_STAGE[FIND_WEBSITE],
        MTURK_STAGE[FIND_HAPPY_HOUR_WEB],
        MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB],
        MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]
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
        if (url == None or url == ''):
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


# Process the assignments from a find website HIT (Stage 0)
# Return the URL agreement percentage and agreed upon URL
def process_find_website_hit_assignments(mturk_location, assignments):
    url_responses = []

    for assignment in assignments:

        if assignment.AssignmentStatus != REJECTED:
            answers = assignment.answers[0]
            url_found = get_answer(answers, WEBSITE_FOUND)
            url = get_answer(answers, WEBSITE_FIELD)
            comments = get_answer(answers, COMMENTS)

            if (url_found == 'yes'):
                url_responses.append(url)
            else:
                url_responses.append('')

            add_comments(mturk_location, comments)

    return get_url_agreement_percentage(url_responses)


# Get whether happy hour was found
# If not, update happy hour attempt count
# If we have wrong website, or wrong phone number, update the stage to reflect it and terminate the happy hour
# acquisition process
def get_happy_hour_found(mturk_location, assignment):
    answers = assignment.answers[0]
    happy_hour_found = get_answer(answers, HAPPY_HOUR_FOUND)
    comments = get_answer(answers, COMMENTS)

    add_comments(mturk_location, comments)

    if happy_hour_found == "yes":
        # Happy hours found
        return True

    elif happy_hour_found == "no":
        # Happy hours not found, but information source is correct
        mturk_location.attempts = int(mturk_location.attempts) + 1
        mturk_location.save()
        return False

    elif happy_hour_found == "wrong-website":
        # Happy hours not found, because we have wrong website
        mturk_location.stage = MTURK_STAGE[WRONG_WEBSITE]
        mturk_location.save()
        return False

    elif happy_hour_found == "wrong-phone-number":
        # Happy hours not found, because we have wrong phone number
        mturk_location.stage = MTURK_STAGE[WRONG_PHONE_NUMBER]
        mturk_location.save()
        return False

    else:
        return False


# Process the assignment from a find website happy hour info HIT (Stage 1)
def process_find_happy_hour_info_assignment(mturk_location, assignment):
    answers = assignment.answers[0]
    mturk_location.deals = get_answer(answers, DEALS)
    mturk_location.save()
    add_comments(mturk_location, get_answer(answers, COMMENTS))


# Process the assignment from a confirm website happy hour info HIT (Stage 2/3)
def process_confirm_happy_hour_info_assignment(mturk_location, assignment):
    answers = assignment.answers[0]
    deals = get_answer(answers, DEALS)

    if deals == mturk_location.deals:
        # If deals hasn't changed, this HIT confirms the previous one.
        mturk_location.confirmations += 1
    else:
        # Otherwise, set confirmations back to 0
        mturk_location.confirmations = 0

    # Update deals
    mturk_location.deals = get_answer(answers, DEALS)
    mturk_location.save()
    add_comments(mturk_location, get_answer(answers, COMMENTS))


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