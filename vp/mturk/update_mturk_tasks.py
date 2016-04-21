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
                if (mturk_location.stat == None):
                    add_mturk_stat(mturk_location, FIND_WEBSITE)

            mturk_location.save()

        else:
            # Evaluate the corresponding HIT assignments for this location if all assignments are complete
            hit = conn.get_hit(mturk_location.hit_id)[0]
            if (hit.HITStatus == REVIEWABLE):
                assignments = conn.get_assignments(hit.HITId)



                elif int(mturk_location.stage) == MTURK_STAGE[FIND_HAPPY_HOUR_WEB]:
                    # Get latest assignment
                    assignment = assignments[-1]
                    happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                    if not happy_hour_found:
                        # If happy hour was not found because we have the wrong website, done.
                        if (mturk_location.stage == MTURK_STAGE[WRONG_WEBSITE]):
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)

                        else:
                            # If we've not maxed out on attempts to get the happy hour info, try again
                            if mturk_location.attempts < MAX_GET_HAPPY_HOUR_WEB_ATTEMPTS:
                                conn.extend_hit(hit.HITId, assignments_increment=1)
                                add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB][PRICE])
                            else:
                                # Otherwise, transfer to phone process
                                mturk_location.hit_id = None
                                mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
                                mturk_location.attempts = 0
                                approve_and_dispose(conn, hit)
                                complete_mturk_stat(mturk_location, False)

                    else:
                        # Happy hour was found. Process response
                        process_find_happy_hour_info_assignment(mturk_location, assignments[-1])
                        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
                        complete_mturk_stat(mturk_location, False)
                        create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])
                        approve_and_dispose(conn, hit)
                        add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_WEB)

                elif int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]) or \
                    int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]):

                    assignment = assignments[-1]
                    happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                    if not happy_hour_found:
                        if (mturk_location.stage == MTURK_STAGE[WRONG_WEBSITE]):
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)

                        else:
                            # Move back to find happy hour stage
                            mturk_location.hit_id = None
                            mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)

                    else:
                        process_confirm_happy_hour_info_assignment(mturk_location, assignments[-1])

                        # If confirmations exceed min required, done!
                        if (mturk_location.confirmations >= 2):
                            mturk_location.stage = MTURK_STAGE[COMPLETE]
                            mturk_location.location.dealDataSource = DATA_SOURCE[WEBSITE]
                            mturk_location.location.save()
                            complete_mturk_stat(mturk_location, True)
                            approve_and_dispose(conn, hit)

                        # Otherwise, go to other confirm stage (to avoid same Turker picking up HIT again
                        else:
                            if (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]):
                                mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]
                                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB_2])

                            else:
                                mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
                                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])

                            add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB][PRICE])
                            approve_and_dispose(conn, hit)

                mturk_location.save()