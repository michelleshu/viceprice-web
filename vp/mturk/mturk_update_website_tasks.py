__author__ = 'michelleshu'

from common_constants import *
from mturk_utilities import *
from boto.mturk import connection
import time
import datetime


# Initialize tasks starting from Stage 1 for new locations to be added
def initialize_tasks(filename):
    conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
    register_hit_types(conn)

    location_objects = get_location_objects_from_csv(filename)

    for location in location_objects:
        create_hit(conn, location, HIT_TYPES[VERIFY_WEBSITE])

    write_location_objects_to_csv(location_objects, UPDATED_WEBSITE_DATA_FILE, append=False)

# Check for HIT completion for all in-progress website tasks and update as necessary
def update_website_tasks():
    conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
    register_hit_types(conn)

    locations_to_update = get_location_objects_from_csv(UPDATED_WEBSITE_DATA_FILE)
    phone_locations_to_add = []

    # Count the number of locations in each stage
    stage_1_count = 0
    stage_3_count = 0
    stage_4_count = 0
    phone_task_count = 0
    complete_count = 0

    for location in locations_to_update:
        if (int(location.stage) == MTURK_STAGE[COMPLETE] or int(location.stage) == MTURK_STAGE[NO_HH_FOUND]):
            complete_count = complete_count + 1
            continue

        if (int(location.stage) == MTURK_STAGE[FIND_PHONE_HH] or int(location.stage) == MTURK_STAGE[CONFIRM_PHONE_HH]):
            phone_task_count = phone_task_count + 1
            continue

        if (int(location.stage) == 1):
            stage_1_count = stage_1_count + 1
        elif(int(location.stage) == 3):
            stage_3_count = stage_3_count + 1
        elif(int(location.stage) == 4):
            stage_4_count = stage_4_count + 1

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
                        location.stage = MTURK_STAGE[FIND_WEBSITE_HH_B]
                        create_hit(conn, location, HIT_TYPES[FIND_WEBSITE_HH_B])

                    elif (agreed_url == ""):
                        location.url_found = False
                        if (location.phone_number != None and location.phone_number != ""):
                            location.stage = MTURK_STAGE[FIND_PHONE_HH]
                            phone_locations_to_add.append(location)
                        else:
                            location.stage = MTURK_STAGE[NO_HH_FOUND]

                    else:
                        location.url_found = True
                        location.url = agreed_url
                        location.stage = MTURK_STAGE[FIND_WEBSITE_HH_B]
                        create_hit(conn, location, HIT_TYPES[FIND_WEBSITE_HH_B])

                    approve_and_dispose(conn, hit)

            elif int(location.stage) == MTURK_STAGE[FIND_WEBSITE_HH_B]:
                happy_hour_found = was_website_hh_found(conn, location, assignments[-1])

                if not happy_hour_found:
                    if location.get_hh_attempts < MAX_GET_HH_ATTEMPTS:
                        conn.extend_hit(hit.HITId, assignments_increment=1)
                    else:
                        location.stage = MTURK_STAGE[FIND_PHONE_HH]
                        phone_locations_to_add.append(location)
                        approve_and_dispose(conn, hit)
                else:
                    processed = process_find_happy_hour_info_assignment(conn, location, assignments[-1])

                    if processed == True:
                        location.stage = MTURK_STAGE[CONFIRM_WEBSITE_HH_B]
                        create_hit(conn, location, HIT_TYPES[CONFIRM_WEBSITE_HH_B])
                        approve_and_dispose(conn, hit)
                    else:
                        conn.extend_hit(hit.HITId, assignments_increment=1)

            elif int(location.stage) == MTURK_STAGE[CONFIRM_WEBSITE_HH_B]:
                confirmed = process_confirm_happy_hour_info_assignment(conn, location, assignments[-1])

                if (confirmed == None):
                    # Failed attention check
                    conn.extend_hit(hit.HITId, assignments_increment=1)
                else:
                    if (confirmed and location.deals_confirmations >= MIN_CONFIRMATIONS):
                        location.stage = MTURK_STAGE[COMPLETE]
                    else:
                        create_hit(conn, location, HIT_TYPES[CONFIRM_WEBSITE_HH_B])

                    approve_and_dispose(conn, hit)

    # Write phone locations to add to phone CSV
    write_location_objects_to_csv(phone_locations_to_add, NEW_PHONE_DATA_FILE, append=True)

    # Remove phone objects from website CSV
    for phone_task in phone_locations_to_add:
        locations_to_update.remove(phone_task)

    # Write updated website objects
    write_location_objects_to_csv(locations_to_update, UPDATED_WEBSITE_DATA_FILE, append=False)

    return [str(stage_1_count), str(stage_3_count), str(stage_4_count), str(complete_count),
            str((float(complete_count) + float(phone_task_count)) / len(locations_to_update))]


def poll_for_website_updates():
    completion_percentage = 0

    with open("temp/website_stats.csv", 'ab') as stats_file:
        filewriter = csv.writer(stats_file)
        filewriter.writerow(["Verify Website", "Find Website HH", "Confirm Website HH", "Complete", "Percent Complete"])
        stats_file.close()

    while float(completion_percentage) < 1.0:
        status = update_website_tasks()
        completion_percentage = status[-1]
        status.insert(0, str(datetime.datetime.now()))
        print("Status: " + str(status))
        with open("temp/website_stats.csv", 'ab') as stats_file:
            filewriter = csv.writer(stats_file)
            filewriter.writerow(status)
            stats_file.close()
        time.sleep(WEBSITE_UPDATE_FREQUENCY)



conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
hits = list(conn.get_all_hits())
for hit in hits:
    conn.disable_hit(hit.HITId)


initialize_tasks('data/initial_test_small.csv')

poll_for_website_updates()