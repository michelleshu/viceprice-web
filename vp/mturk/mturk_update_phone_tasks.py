from mturk_utilities import *
from django.conf import settings
from django.utils import timezone
from boto.mturk import connection
from boto.mturk import price

# Check for HIT completion for all in-progress phone tasks and update as necessary
def update():

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    register_hit_types(conn)

    # Get the phone updates in progress
    locations_to_update = get_phone_update_mturk_locations()

    for mturk_location in locations_to_update:

        # If there is no HIT for the location, create one
        if (mturk_location.hit_id == None):
            if within_business_hours(mturk_location.location.id):
                if (mturk_location.stage == MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]):
                    create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE])
                    if (mturk_location.stat == None):
                        add_mturk_stat(mturk_location, FIND_HAPPY_HOUR_PHONE)

                elif (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]):
                    create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])
                    if (mturk_location.stat == None):
                        add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_PHONE)

                elif (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE_2]):
                    create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE_2])

                mturk_location.save()

        else:
            # Evaluate the corresponding HIT assignments for this location if all assignments are complete
            hit = conn.get_hit(mturk_location.hit_id)[0]
            if (hit.HITStatus == REVIEWABLE):
                assignments = conn.get_assignments(hit.HITId)

                # Process assignments depending on current stage of HIT
                if int(mturk_location.stage) == MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]:
                    # Get latest assignment
                    assignment = assignments[-1]
                    happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                    if not happy_hour_found:
                        # If happy hour was not found because we have the wrong phone number, done
                        if (mturk_location.stage == MTURK_STAGE[WRONG_PHONE_NUMBER]):
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)
                        else:
                            # If we've not maxed out on attempts to get the happy hour info, try again
                            if mturk_location.attempts < MAX_GET_HAPPY_HOUR_PHONE_ATTEMPTS:
                                add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE][PRICE])

                                if (within_business_hours(mturk_location.location.id)):
                                    conn.extend_hit(hit.HITId, assignments_increment=1)
                                else:
                                    # Outside of business hours, cancel and restart tomorrow
                                    approve_and_dispose(conn, hit)
                                    mturk_location.hit_id = None

                            else:
                                # Otherwise, transfer to No Info. Done.
                                mturk_location.hit_id = None
                                mturk_location.stage = MTURK_STAGE[NO_INFO]
                                approve_and_dispose(conn, hit)
                                complete_mturk_stat(mturk_location, False)

                    else:
                        # Happy hour was found. Process response
                        process_find_happy_hour_info_assignment(mturk_location, assignments[-1])
                        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]

                        conn.grant_bonus(assignment.WorkerId, assignment.AssignmentId,
                            price.Price(amount=settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE][BONUS]), "Successful phone call")
                        approve_and_dispose(conn, hit)

                        add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE][BONUS])
                        complete_mturk_stat(mturk_location, False)
                        add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_PHONE)

                        if (within_business_hours(mturk_location.location.id)):
                            create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])
                        else:
                            mturk_location.hit_id = None

                elif int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]) or \
                    int(mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE_2]):

                    assignment = assignments[-1]
                    happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                    if not happy_hour_found:
                        if (mturk_location.stage == MTURK_STAGE[WRONG_PHONE_NUMBER]):
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)

                        else:
                            # Move back to find happy hour stage
                            mturk_location.hit_id = None
                            mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
                            complete_mturk_stat(mturk_location, False)
                            approve_and_dispose(conn, hit)

                    else:
                        # Happy Hour Found
                        process_confirm_happy_hour_info_assignment(mturk_location, assignments[-1])

                        conn.grant_bonus(assignment.WorkerId, assignment.AssignmentId,
                            price.Price(amount=settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE][BONUS]), "Successful phone call")
                        approve_and_dispose(conn, hit)

                        add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE][BONUS])

                        # If confirmations exceed min required, done!
                        if (mturk_location.confirmations >= 2):
                            mturk_location.stage = MTURK_STAGE[COMPLETE]
                            mturk_location.location.dealDataSource = DATA_SOURCE[PHONE]
                            mturk_location.location.save()
                            complete_mturk_stat(mturk_location, True)

                        # Otherwise, go to other confirm stage (to avoid same Turker picking up HIT again
                        else:
                            if (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]):
                                mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE_2]
                                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE_2])

                            else:
                                mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]
                                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])

                            add_mturk_stat_cost(mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE][PRICE])


                mturk_location.save()