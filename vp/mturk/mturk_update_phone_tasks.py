from mturk_utilities import *
from django.conf import settings
from django.utils import timezone
from boto.mturk import connection

# Check for HIT completion for all in-progress phone tasks and update as necessary
def update():

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    register_hit_types(conn)

    # Get the website updates in progress
    locations_to_update = get_phone_update_mturk_locations()

    for mturk_location in locations_to_update:

        # If there is no HIT for the location, create one
        if (mturk_location.hit_id == None): # and within_business_hours
            if (mturk_location.stage == MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]):
                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE])
                add_mturk_stat(mturk_location, FIND_HAPPY_HOUR_PHONE)
            elif (mturk_location.stage == MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]):
                create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])

            mturk_location.save()
            continue

        # Evaluate the corresponding HIT assignments for this location if all assignments are complete
        hit = conn.get_hit(mturk_location.hit_id)[0]
        if (hit.HITStatus == REVIEWABLE):
            assignments = conn.get_assignments(hit.HITId)

            # if (not within_business_hours(location.foursquareId)):
            #     # Outside of business hours, cancel HIT and restart tomorrow
            #     approve_and_dispose(conn, hit)
            #     location.hit_id = None
            #     location.save()
            #     continue

            # Process assignments depending on current stage of HIT
            if int(mturk_location.stage) == MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]:
                # Get latest assignment
                assignment = assignments[-1]

                happy_hour_found = get_happy_hour_found(mturk_location, assignment)

                if (int(location.stage) == MTURK_STAGE[FIND_PHONE_HH]):
                    extended = extend_if_not_reachable(conn, location, assignments)

                    if not extended:
                        correct_number = process_find_happy_hour_info_assignment_phone(conn, location, assignments[-1])

                        if correct_number == None:
                            # Failed attention check
                            conn.extend_hit(hit.HITId, assignments_increment=1)

                        else:
                            if (int(location.stage) == MTURK_STAGE[CONFIRM_PHONE_HH]):
                                create_hit(conn, location, HIT_TYPES[CONFIRM_PHONE_HH])
                                approve_and_dispose(conn, hit)

                            if (not correct_number):
                                location.stage = MTURK_STAGE[NO_HH_FOUND]
                                location.comments = "Incorrect phone number"
                                approve_and_dispose(conn, hit)

                    else:
                        if len(assignments) >= PHONE_UNREACHABLE_LIMIT:
                            approve_and_dispose(conn, hit)

                elif int(location.stage) == MTURK_STAGE[CONFIRM_PHONE_HH]:
                    extended = extend_if_not_reachable(conn, location, assignments)

                    if not extended:
                        confirmed = process_confirm_happy_hour_info_assignment(conn, location, assignments[-1])

                        if (confirmed and location.deals_confirmations >= MIN_CONFIRMATIONS):
                            if (has_happy_hour_data(location)):
                                location.data_source = DATA_SOURCE[PHONE]
                                location.stage = MTURK_STAGE[COMPLETE]
                                location.update_completed = timezone.now()
                            else:
                                # If no valid data, move to no data found
                                location.stage = MTURK_STAGE[NO_HH_FOUND]
                        else:
                            create_hit(conn, location, HIT_TYPES[CONFIRM_PHONE_HH])

                        approve_and_dispose(conn, hit)

                location.save()