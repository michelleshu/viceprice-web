__author__ = 'michelleshu'

from mturk_utilities import *
from django.conf import settings
from django.utils import timezone
from boto.mturk import connection
import json


# Check for HIT completion for all in-progress website tasks and update as necessary
def update():

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    register_hit_types(conn)

    # Get the website updates in progress
    locations_to_update = MTurkLocationInfo.objects.all()

    # Add new locations that can be updated
    add_mturk_locations_to_update(conn)

    for mturk_location in locations_to_update:

        # If there is no HIT for the location, create one
        if (mturk_location.hit_id == None):
            create_hit(conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR])
            mturk_location.save()

        else:
            # Evaluate the corresponding HIT assignments for this location if all assignments are complete
            hit = conn.get_hit(mturk_location.hit_id)[0]
            if (hit.HITStatus == REVIEWABLE):
                assignments = conn.get_assignments(hit.HITId)
                deal_jsons = []
                comments = []

                for assignment in assignments:
                    if assignment.AssignmentStatus != REJECTED:
                        answers = assignment.answers[0]
                        deals_result = get_answer(answers, DEALS_RESULT)
                        comments = get_answer(answers, COMMENTS)

                        deal_jsons.append(json.loads(deals_result))

                if len(deal_jsons) > (len(assignments) / 2):
                    match_result = get_match_percentage(deal_jsons)
                    print(match_result[0])
                    print(match_result[1])
                    print(match_result[2][0])


def get_match_percentage(deal_jsons):
    max_match_percentage = 0.0
    max_matches_deal_json = None
    max_matches_matching_deals = None

    for i in range(0, len(deal_jsons)):

        current_deal_json = deal_jsons[i]
        current_matching_deals = []

        for j in range(0, len(deal_jsons)):
            if i != j:
                matching_deals = deals_responses_match(current_deal_json, deal_jsons[j])

                if matching_deals != None:
                    current_matching_deals.append(matching_deals)

        match_percentage = float(len(current_matching_deals) + 1) / float(len(deal_jsons))

        if match_percentage > max_match_percentage:
            max_match_percentage = match_percentage
            max_matches_deal_json = current_deal_json
            max_matches_matching_deals = current_matching_deals

    return (max_match_percentage, max_matches_deal_json, max_matches_matching_deals)


# Check to see if two sets of deals from two different Turkers match.
# Matching requires that for every deal detail, the price, deal type and drink category are the same
# And the time ranges match up as well.
def deals_responses_match(deal_json_a, deal_json_b):
    matching_deal_responses = []

    if len(deal_json_a["dealData"]) == len(deal_json_b["dealData"]):

        for deal_data in deal_json_a["dealData"]:
            deal_details_b = get_deal_details_for_time_frame(deal_data["daysOfWeek"], deal_data["timePeriods"], deal_json_b)

            if deal_details_b != None:
                matches = deal_details_match(deal_data["dealDetails"], deal_details_b)

                if matches != None:
                    matching_deal_responses.append(matches)

    if len(matching_deal_responses) == len(deal_json_a["dealData"]):
        return matching_deal_responses

    return None


# Retrieve the deal details that match a certain days of week/time frame combination
def get_deal_details_for_time_frame(days_of_week, time_periods, deal_json):

    for deal_data in deal_json["dealData"]:

        if len(deal_data["daysOfWeek"]) != len(days_of_week):
            continue

        for i in range(0, len(days_of_week)):
            if (deal_data["daysOfWeek"][i] != days_of_week[i]):
                continue

        if len(deal_data["timePeriods"]) != len(time_periods):
            continue

        if len(time_periods) == 1:
            if (time_periods[0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) or \
                (time_periods[0]["endTime"] != deal_data["timePeriods"][0]["endTime"]):
                continue

        else: # length = 2
            if (time_periods[0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) and \
                (time_periods[0]["startTime"] != deal_data["timePeriods"][1]["startTime"]):
                continue

            if (time_periods[1]["endTime"] != deal_data["timePeriods"][0]["endTime"]) and \
                (time_periods[1]["endTime"] != deal_data["timePeriods"][1]["endTime"]):
                continue

        return deal_data["dealDetails"]

    return None


# If deal details set from A completely matches deal details set from B,
# return the deal details from B in order corresponding to those from A
def deal_details_match(deal_details_a, deal_details_b):
    matches = []

    if (len(deal_details_a) == len(deal_details_b)):
        for deal_detail in deal_details_a:
            for match_candidate in deal_details_b:
                if deal_detail["category"] != match_candidate["category"]:
                    continue
                if deal_detail["dealType"] != match_candidate["dealType"]:
                    continue
                if deal_detail["dealValue"] != match_candidate["dealValue"]:
                    continue

                # Match found - save it
                matches.append(match_candidate)

    if len(matches) == len(deal_details_a):
        return matches

    return None