__author__ = 'michelleshu'

from mturk_utilities import *
from django.conf import settings
from django.utils import timezone
from boto.mturk import connection


# Check for HIT completion for all in-progress website tasks and update as necessary
def update():

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    register_hit_types(conn)

    # Get the website updates in progress
    locations_to_update = get_website_update_mturk_locations()

    # Add new locations that can be updated
    add_mturk_locations_to_update(conn)

    for mturk_location in locations_to_update:

        # If there is no HIT for the location, create one
        if (mturk_location.hit_id == None):
            if (mturk_location.stage == MTURK_STAGE[FIND_WEBSITE]):
                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])
            elif (mturk_location.stage == MTURK_STAGE[FIND_HAPPY_HOUR_WEB]):
                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])
            elif (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]):
                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])

        # Evaluate the corresponding HIT assignments for this location if all assignments are complete
        hit = conn.get_hit(mturk_location.hit_id)[0]
        if (hit.HITStatus == REVIEWABLE):
            assignments = conn.get_assignments(hit.HITId)

            # Process assignments depending on current stage of HIT
            if int(mturk_location.stage) == MTURK_STAGE[FIND_WEBSITE]:
                url_agreement_info = process_find_website_hit_assignments(mturk_location, assignments)
                agreement_percentage = url_agreement_info[0]
                agreed_url = url_agreement_info[1]

                if (agreement_percentage < MIN_AGREEMENT_PERCENTAGE):
                    # Extend the HIT as long as possible to get agreement
                    if len(assignments) < MAX_ASSIGNMENTS_TO_PUBLISH:
                        conn.extend_hit(hit.HITId, assignments_increment=1)
                    # If exceeds max assignment number allowed by Amazon, we must make a new HIT
                    else:
                        conn.disable_hit(hit.HITId)
                        create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])
                else:
                    # If no URL found, continue to phone stage if possible. Forfeit if not.
                    if (agreed_url == '' or agreed_url == None):
                        if (mturk_location.phone_number != None and mturk_location.phone_number != ''):
                            mturk_location.hit_id = None
                            mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
                        else:
                            mturk_location.stage = MTURK_STAGE[NO_INFO]
                            mturk_location.update_completed = timezone.now()

                    else:
                        mturk_location.website = agreed_url
                        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
                        create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])

                    approve_and_dispose(conn, hit)

            elif int(mturk_location.stage) == MTURK_STAGE[FIND_HAPPY_HOUR_WEB]:
                # Get latest assignment
                assignment = assignments[-1]

                happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                if not happy_hour_found:
                    # If happy hour was not found because we have the wrong website or wrong phone number, done.
                    if (mturk_location.stage == MTURK_STAGE[WRONG_WEBSITE] or
                        mturk_location.stage == MTURK_STAGE[WRONG_PHONE_NUMBER]):
                        approve_and_dispose(conn, hit)

                    else:
                        # If we've not maxed out on attempts to get the happy hour info, try again
                        if mturk_location.attempts < MAX_GET_HAPPY_HOUR_WEB_ATTEMPTS:
                            conn.extend_hit(hit.HITId, assignments_increment=1)
                        else:
                            # Otherwise, transfer to phone process
                            mturk_location.hit_id = None
                            mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
                            mturk_location.attempts = 0
                            approve_and_dispose(conn, hit)

                else:
                    # Happy hour was found. Process response
                    process_find_happy_hour_info_assignment(mturk_location, assignments[-1])
                    mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
                    create_hit(conn, mturk_location.settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])
                    approve_and_dispose(conn, hit)

            elif int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]) or \
                int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]):

                assignment = assignments[-1]
                happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                if not happy_hour_found:
                    if (mturk_location.stage == MTURK_STAGE[WRONG_WEBSITE] or
                        mturk_location.stage == MTURK_STAGE[WRONG_PHONE_NUMBER]):
                        approve_and_dispose(conn, hit)

                    else:
                        # Move back to find happy hour stage
                        mturk_location.hit_id = None
                        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
                        approve_and_dispose(conn, hit)

                else:
                    process_confirm_happy_hour_info_assignment(mturk_location, assignments[-1])

                    # If confirmations exceed min required, done!
                    if (mturk_location.confirmations >= 2):
                        mturk_location.stage = MTURK_STAGE[COMPLETE]



            #
            # elif int(location.stage) == MTURK_STAGE[CONFIRM_WEBSITE_HH]:
            #     confirmed = process_confirm_happy_hour_info_assignment(conn, location, assignments[-1])
            #
            #     if (confirmed == None):
            #         # Failed attention check
            #         conn.extend_hit(hit.HITId, assignments_increment=1)
            #     else:
            #         if (confirmed and location.deals_confirmations >= MIN_CONFIRMATIONS):
            #             if (has_happy_hour_data(location)):
            #                 location.data_source = DATA_SOURCE[WEBSITE]
            #                 location.stage = MTURK_STAGE[COMPLETE]
            #                 location.update_completed = timezone.now()
            #             else:
            #                 # Move to phone process if the stage completes with no valid data
            #                 location.stage = MTURK_STAGE[FIND_PHONE_HH]
            #         else:
            #             create_hit(conn, location, HIT_TYPES[CONFIRM_WEBSITE_HH])
            #
            #         approve_and_dispose(conn, hit)

            mturk_location.save()