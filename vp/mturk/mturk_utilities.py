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
def add_mturk_locations_to_update(conn):
    earliest_unexpired_date = timezone.now() - datetime.timedelta(days=settings.EXPIRATION_PERIOD)

    new_locations = []
    if not settings.MTURK_TEST_MODE:
        # For tests, only evaluate the MTurkLocationInfos added in test. Do not add new ones here.
        # Otherwise, in production mode, this is the query for all locations that are to be added to the MTurk update
        # process.
        new_locations = Location.objects.filter(dateLastUpdated__lt=earliest_unexpired_date) \
            .filter(happyHourWebsite__isnull=False).all()

    # Add new locations to MTurkLocationInfo
    for location in new_locations:
        mturk_location = MTurkLocationInfo(
            location = location,
            name = location.name,
            address = location.street,
            phone_number = location.formattedPhoneNumber,
            website = location.happyHourWebsite
        )
        mturk_location.save()

        add_mturk_stat(mturk_location)

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.dateLastUpdated = timezone.now()
        location.mturkNoDealData = False
        location.mturkDataCollectionFailed = False
        location.mturkDataCollectionAttempts = 1
        location.save()
        
    respawn_locations = Location.objects.filter(mturkDataCollectionFailed = True) \
        .filter(happyHourWebsite__isnull=False) \
        .filter(mturkDataCollectionAttempts__lt=3).all()
    
    for location in respawn_locations:

        mturk_location = MTurkLocationInfo(
            location = location,
            name = location.name,
            address = location.street,
            phone_number = location.formattedPhoneNumber,
            website = location.happyHourWebsite
        )
        mturk_location.save()

        add_mturk_stat(mturk_location)

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.dateLastUpdated = timezone.now()
        location.mturkDataCollectionFailed = False
        location.mturkDataCollectionAttempts += 1
        location.save()


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
        if hit_type[LOCALE_REQUIRED]:
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
    # Use qualifications: MIN_PERCENTAGE_APPROVED, MIN_HITS_COMPLETED and optionally LOCALE_REQUIRED
    min_percentage_qualification = PercentAssignmentsApprovedRequirement(
        "GreaterThan", settings.MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED, required_to_preview=True)
    min_hits_completed_qualification = NumberHitsApprovedRequirement(
        "GreaterThan", settings.MIN_HITS_COMPLETED, required_to_preview=True)

    qualifications = Qualifications()
    qualifications.add(min_percentage_qualification)
    qualifications.add(min_hits_completed_qualification)
    if hit_type[LOCALE_REQUIRED] != None:
        locale_qualification = LocaleRequirement(
            "EqualTo", hit_type[LOCALE_REQUIRED], required_to_preview=True)
        qualifications.add(locale_qualification)

    layout_parameter_names = hit_type[LAYOUT_PARAMETER_NAMES]

    layout_parameters = []
    for parameter_name in layout_parameter_names:
        parameter_value = getattr(mturk_location_info, parameter_name)
        if parameter_value != None and (isinstance(parameter_value, str) or isinstance(parameter_value, unicode)):
            # Handle string replacements so names play well with MTurk
            parameter_value = parameter_value.replace("<", "&lt;").replace("&", "%26")

        layout_parameters.append(LayoutParameter(parameter_name, parameter_value))

    hit = conn.create_hit(
        hit_type=hit_type[HIT_TYPE_ID],
        question=None,
        hit_layout=hit_type[LAYOUT_ID],
        lifetime=hit_type[LIFETIME],
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

# Approve assignments from HIT and dispose of the HIT
def approve_and_dispose(conn, hit):
    if (hit.HITStatus == REVIEWABLE):
        for assignment in conn.get_assignments(hit.HITId):
            if (assignment.AssignmentStatus == SUBMITTED):
                conn.approve_assignment(assignment.AssignmentId)

        conn.dispose_hit(hit.HITId)

def extend(conn, hit, mturk_location, assignments = 3):
    conn.extend_hit(hit.HITId, assignments_increment=3)

    if (mturk_location.stat != None):
        mturk_location.stat.numberOfAssignments += assignments
        mturk_location.stat.save()

#endregion

#region Metadata Collection

def add_mturk_stat(mturk_location):
    hit_type = settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR]

    stat = MTurkLocationInfoStat(
        location=mturk_location.location,
        dateStarted=timezone.now(),
        numberOfAssignments = hit_type[MAX_ASSIGNMENTS],
        costPerAssignment=hit_type[PRICE],
        minAgreementPercentage=settings.MIN_AGREEMENT_PERCENTAGE,
        minPercentagePreviousAssignmentsApproved=settings.MIN_PERCENTAGE_PREVIOUS_ASSIGNMENTS_APPROVED,
        minHITsCompleted=settings.MIN_HITS_COMPLETED,
        localeRequired=hit_type[LOCALE_REQUIRED]
    )
    stat.save()

    mturk_location.stat = stat
    mturk_location.save()


def complete_mturk_stat(mturk_location, data_found):
    mturk_location.stat.happyHourDataFound = data_found
    mturk_location.stat.dateCompleted = timezone.now()
    mturk_location.stat.save()
    mturk_location.stat = None
    mturk_location.save()

#endregion