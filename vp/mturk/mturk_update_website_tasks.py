__author__ = 'michelleshu'

from mturk_utilities import *
from django.utils import timezone
from boto.mturk import connection


# Check for HIT completion for all in-progress website tasks and update as necessary
def update():

    conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
    register_hit_types(conn)

    # Get the website updates in progress
    locations_to_update = get_website_update_locations()

    # Add new locations that can be updated
    add_mturk_locations_to_update(conn)

    for location in locations_to_update:

        # Evaluate the corresponding HIT assignments for this location if all assignments are complete
        hit = conn.get_hit(location.hit_id)[0]
        if (hit.HITStatus == REVIEWABLE):
            assignments = conn.get_assignments(hit.HITId)

            # Process assignments depending on current stage of HIT
            if int(location.stage) == MTURK_STAGE[VERIFY_WEBSITE]:
                url_agreement_info = process_verify_website_hit_assignments(conn, location, assignments)

                if (url_agreement_info == None):
                    continue

                agreement_percentage = url_agreement_info[0]
                agreed_url = url_agreement_info[1]

                if (agreement_percentage < MIN_AGREEMENT_PERCENTAGE):
                    # Extend the HIT as long as possible to get agreement
                    if len(assignments) < MAX_ASSIGNMENTS_TO_PUBLISH:
                        conn.extend_hit(hit.HITId, assignments_increment=1)
                    # If exceeds max assignment number allowed by Amazon, we must make a new HIT
                    else:
                        conn.disable_hit(hit.HITId)
                        create_hit(conn, location, HIT_TYPES[VERIFY_WEBSITE])
                else:
                    # Update with URL information retrieved
                    if (agreed_url == CONFIRMED_RESPONSE):
                        location.url_provided_verified = True
                        location.url = location.url_provided
                        location.stage = MTURK_STAGE[FIND_WEBSITE_HH]
                        create_hit(conn, location, HIT_TYPES[FIND_WEBSITE_HH])

                    elif (agreed_url == "" or agreed_url == None):
                        location.url_found = False
                        if (location.phone_number != None and location.phone_number != ""):
                            location.hit_id = None
                            location.stage = MTURK_STAGE[FIND_PHONE_HH]
                        else:
                            location.stage = MTURK_STAGE[NO_HH_FOUND]
                            location.update_completed = timezone.now()

                    else:
                        location.url_found = True
                        location.url = agreed_url
                        location.stage = MTURK_STAGE[FIND_WEBSITE_HH]
                        create_hit(conn, location, HIT_TYPES[FIND_WEBSITE_HH])

                    approve_and_dispose(conn, hit)

            elif int(location.stage) == MTURK_STAGE[FIND_WEBSITE_HH]:
                happy_hour_found = was_website_hh_found(conn, location, assignments[-1])

                if not happy_hour_found:
                    if location.get_hh_attempts < MAX_GET_HH_ATTEMPTS:
                        conn.extend_hit(hit.HITId, assignments_increment=1)
                    else:
                        location.hit_id = None
                        location.stage = MTURK_STAGE[FIND_PHONE_HH]
                        approve_and_dispose(conn, hit)
                else:
                    processed = process_find_happy_hour_info_assignment(conn, location, assignments[-1])

                    if processed == True:
                        location.stage = MTURK_STAGE[CONFIRM_WEBSITE_HH]
                        create_hit(conn, location, HIT_TYPES[CONFIRM_WEBSITE_HH])
                        approve_and_dispose(conn, hit)
                    else:
                        conn.extend_hit(hit.HITId, assignments_increment=1)

            elif int(location.stage) == MTURK_STAGE[CONFIRM_WEBSITE_HH]:
                confirmed = process_confirm_happy_hour_info_assignment(conn, location, assignments[-1])

                if (confirmed == None):
                    # Failed attention check
                    conn.extend_hit(hit.HITId, assignments_increment=1)
                else:
                    if (confirmed and location.deals_confirmations >= MIN_CONFIRMATIONS):
                        location.data_source = DATA_SOURCE[WEBSITE]
                        location.stage = MTURK_STAGE[COMPLETE]
                        location.update_completed = timezone.now()
                    else:
                        create_hit(conn, location, HIT_TYPES[CONFIRM_WEBSITE_HH])

                    approve_and_dispose(conn, hit)

            location.comments = location.comments[:999]
            location.save()