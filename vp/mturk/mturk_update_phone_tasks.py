from mturk_utilities import *
from django.utils import timezone
from boto.mturk import connection

# Check for HIT completion for all in-progress phone tasks and update as necessary
def update():

    conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
    register_hit_types(conn)

    # Get the website updates in progress
    locations_to_update = get_phone_update_locations()

    for location in locations_to_update:

        # Evaluate the corresponding HIT assignments for this location if all assignments are complete
        hit = conn.get_hit(location.hit_id)[0]
        if (hit.HITStatus == REVIEWABLE):
            assignments = conn.get_assignments(hit.HITId)

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
                            approve_and_dispose(conn, hit)

            elif int(location.stage) == MTURK_STAGE[CONFIRM_PHONE_HH]:
                extended = extend_if_not_reachable(conn, location, assignments)

                if not extended:
                    confirmed = process_confirm_happy_hour_info_assignment(conn, location, assignments[-1])

                    if (confirmed and location.deals_confirmations >= MIN_CONFIRMATIONS):
                        location.data_source = DATA_SOURCE[PHONE]
                        location.stage = MTURK_STAGE[COMPLETE]
                        location.update_completed = timezone.now()
                    else:
                        create_hit(conn, location, HIT_TYPES[CONFIRM_PHONE_HH])

                    approve_and_dispose(conn, hit)

            location.save()