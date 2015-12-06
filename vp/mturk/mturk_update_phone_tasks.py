__author__ = 'michelleshu'

from mturk_utilities import *
from boto.mturk import connection
import os

# Check for HIT completion for all in-progress phone tasks and update as necessary
def update():
    conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
    register_hit_types(conn)

    # Create HITs for the new locations to add to the phone process
    if os.path.isfile(NEW_PHONE_DATA_FILE):
        locations_to_add = get_location_objects_from_csv(NEW_PHONE_DATA_FILE)
        os.remove(NEW_PHONE_DATA_FILE)
    else:
        locations_to_add = []

    for location in locations_to_add:
        create_hit(conn, location, HIT_TYPES[FIND_PHONE_HH])

    # Update existing tasks
    if os.path.isfile(UPDATED_PHONE_DATA_FILE):
        locations_to_update = get_location_objects_from_csv(UPDATED_PHONE_DATA_FILE)
    else:
        locations_to_update = []

    # Count the number of locations in each stage
    stage_5_count = 0
    stage_6_count = 0
    complete_count = 0

    for location in locations_to_update:
        if (int(location.stage) == MTURK_STAGE[COMPLETE] or int(location.stage) == MTURK_STAGE[NO_HH_FOUND]):
            complete_count = complete_count + 1
            continue

        if (int(location.stage) == 5):
            stage_5_count = stage_5_count + 1
        elif(int(location.stage) == 6):
            stage_6_count = stage_6_count + 1

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
                        location.stage = MTURK_STAGE[COMPLETE]
                    else:
                        create_hit(conn, location, HIT_TYPES[CONFIRM_PHONE_HH])

                    approve_and_dispose(conn, hit)

    # Add new phone locations to locations to update
    for new_location in locations_to_add:
        locations_to_update.append(new_location)

    # Write updates to CSV
    write_location_objects_to_csv(locations_to_update, UPDATED_PHONE_DATA_FILE, append=False)

    completion_percentage = 0.0
    if len(locations_to_update) > 0:
        completion_percentage = float(complete_count) / len(locations_to_update)

    return [str(stage_5_count), str(stage_6_count), str(complete_count), str(completion_percentage)]

def update_phone_tasks():
    status = update()
    status.insert(0, str(datetime.datetime.now()))
    print("Status: " + str(status))
    with open("temp/phone_stats.csv", 'ab') as stats_file:
        filewriter = csv.writer(stats_file)
        filewriter.writerow(status)
        stats_file.close()