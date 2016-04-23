__author__ = 'michelleshu'

from boto.mturk import price
from boto.mturk.layoutparam import *
from boto.mturk.qualification import *
import datetime
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from pprint import pprint
from vp.models import Location, MTurkLocationInfo, MTurkLocationInfoStat
from viceprice.constants import *

'''
mturk_utilities.py
This file contains the main utility functions for adding tasks and retrieving updates on location information from MTurk
'''


#region Get locations for update

# Add locations to update process that need to be updated
def add_mturk_locations_to_update(conn, max_to_add = None):
    if (max_to_add == None):
        max_to_add = settings.MAX_LOCATIONS_TO_UPDATE

    currently_updating = MTurkLocationInfo.objects.all().count()

    max_new_locations = max_to_add - currently_updating

    # Get at most max_new_locations locations that have either just been added or expired
    earliest_unexpired_date = timezone.now() - datetime.timedelta(days=settings.EXPIRATION_PERIOD)

    new_locations = Location.objects.filter(Q(mturkDateLastUpdated__lt=earliest_unexpired_date) | Q(mturkDateLastUpdated=None))[0:max_new_locations]

    # new_locations = Location.objects.filter(Q(id__in=test_ids) &
    #                 Q(mturkDateLastUpdated__lt=earliest_unexpired_date))[0:max_new_locations]

    # new_locations = Location.objects.filter(
    #     mturkDateLastUpdated__lt=earliest_unexpired_date)[0:max_new_locations]

    # Add new Foursquare locations to MTurkLocationInfo
    for location in new_locations:

        mturk_location = MTurkLocationInfo(
            location = location,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            website = location.website
        )

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.mturkDateLastUpdated = timezone.now()
        location.save()

        mturk_location.save()

#endregion

#region HIT Creation and Updates

# Register HIT Types with Mechanical Turk and save off HIT type IDs
def register_hit_types(conn):

    for hit_type_name in settings.MTURK_HIT_TYPES:
        hit_type = settings.MTURK_HIT_TYPES[hit_type_name]

        min_percentage_qualification = PercentAssignmentsApprovedRequirement(
            "GreaterThan", settings.MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED, required_to_preview=True)
        min_hits_completed_qualification = NumberHitsApprovedRequirement(
            "GreaterThan", settings.MIN_HITS_COMPLETED, required_to_preview=True)
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
        "GreaterThan", settings.MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED, required_to_preview=True)
    min_hits_completed_qualification = NumberHitsApprovedRequirement(
        "GreaterThan", settings.MIN_HITS_COMPLETED, required_to_preview=True)
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
        elif comments not in mturk_location.comments:
            mturk_location.comments = mturk_location.comments + '\n' + comments

        mturk_location.comments = mturk_location.comments[:999]
        mturk_location.save()
\
# Approve assignments from HIT and dispose of the HIT
def approve_and_dispose(conn, hit):
    if (hit.HITStatus == REVIEWABLE):
        for assignment in conn.get_assignments(hit.HITId):
            if (assignment.AssignmentStatus == SUBMITTED):
                conn.approve_assignment(assignment.AssignmentId)

        conn.dispose_hit(hit.HITId)

#endregion

# Check to see whether we are within valid business hours for a location
def within_business_hours(location_id):
    now = timezone.localtime(timezone.now())
    current_day = now.isoweekday()
    current_time = now.time()

    business_hour_ids = Location.objects.get(id = location_id).businessHours.all().values_list('id', flat=True)
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

    return start_cutoff <= time and end_cutoff >= time


#region Metadata Collection

def add_mturk_stat(mturk_location, stage_name):
    hit_type = settings.MTURK_HIT_TYPES[stage_name]

    stat = MTurkLocationInfoStat(
        dateStarted=timezone.now(),
        location=mturk_location.location,
        costForStage=hit_type[PRICE] * hit_type[MAX_ASSIGNMENTS],
        costPerAssignment=hit_type[PRICE] * hit_type[MAX_ASSIGNMENTS]
    )
    stat.save()

    mturk_location.stat = stat
    mturk_location.save()


def complete_mturk_stat(mturk_location, data_confirmed):
    mturk_location.stat.dateCompleted = timezone.now()
    mturk_location.stat.save()
    mturk_location.stat = None
    mturk_location.save()


#endregion