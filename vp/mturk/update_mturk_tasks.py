__author__ = 'michelleshu'

from mturk_utilities import *
import django
from django.conf import settings
from django.utils import timezone
from boto.mturk import connection
from vp.models import ActiveHour, Location, Deal, DealDetail, MTurkDrinkNameOption
import json

# Check for HIT completion for all in-progress website tasks and update as necessary
def update():

    django.setup()

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
                        deals_result = json.loads(get_answer(answers, DEALS_RESULT))

                        if deals_result["dealsFound"]:
                            deal_jsons.append(deals_result)

                            if get_answer(answers, COMMENTS) != None:
                                comments.append(get_answer(answers, COMMENTS))

                # Require that at least half of responses to contain data
                if len(deal_jsons) > (len(assignments) / 2):
                    merged = merge_deal_jsons(deal_jsons)

                    print("Merged")
                    print(merged)

                    # If able to match enough answers, save the HIT results
                    # if (match_result[0] > (float(settings.MIN_AGREEMENT_PERCENTAGE) / 100.0)) and len(deal_jsons) >= settings.MIN_RESPONSES:
                    #     comment_string = ("\n".join(comments))[:1000]
                    #     save_results(mturk_location.location, match_result[1], match_result[2], comment_string)
                    #
                    #     if mturk_location.stat != None:
                    #         complete_mturk_stat(mturk_location, True)
                    #
                    #     approve_and_dispose(conn, hit)
                    #     mturk_location.location.mturkDataCollectionFailed = False
                    #     mturk_location.location.mturkDateLastUpdated = timezone.now()
                    #     mturk_location.location.save()
                    #     mturk_location.delete()
                    #
                    # # Otherwise, if max number of assignments has not been reached, extend the HIT
                    # elif len(assignments) < settings.MAX_ASSIGNMENTS_TO_PUBLISH:
                    #     extend(conn, hit, mturk_location)
                    #
                    # else:
                    #     # Fail the HIT since we cannot exceed max number of assignments on Amazon
                    #     if mturk_location.stat != None:
                    #         complete_mturk_stat(mturk_location, False)
                    #
                    #     approve_and_dispose(conn, hit)
                    #     mturk_location.location.mturkDataCollectionFailed = True
                    #     mturk_location.location.mturkDateLastUpdated = timezone.now()
                    #     mturk_location.location.save()
                    #     mturk_location.delete()

                else:
                    # Not enough people found a result. Fail the HIT.
                    if mturk_location.stat != None:
                        complete_mturk_stat(mturk_location, False)

                    approve_and_dispose(conn, hit)
                    mturk_location.location.mturkDataCollectionFailed = True
                    mturk_location.location.mturkDateLastUpdated = timezone.now()
                    mturk_location.location.save()
                    mturk_location.delete()


def save_results(location, deal_json, matching_deals, comments):

    # Remove old deals
    previous_deals = location.deals.all()
    location.deals.remove()
    previous_deals.delete()

    for i in range(len(deal_json["dealData"])):
        deal = Deal(
            description = "",
            dealSource = DATA_SOURCES[MTURK],
            comments = comments,
            confirmed = False
        )
        deal.save()

        location.deals.add(deal)
        location.save()

        deal_data = deal_json["dealData"][i]

        for day_of_week in deal_data["daysOfWeek"]:
            for time_frame in deal_data["timePeriods"]:

                end_time = time_frame["endTime"]
                if time_frame["untilClose"]:
                    end_time = None

                active_hour = ActiveHour(
                    dayofweek = day_of_week,
                    start = time_frame["startTime"],
                    end = end_time
                )

                active_hour.save()
                deal.activeHours.add(active_hour)

        for j in range(len(deal_data["dealDetails"])):

            deal_detail_data = deal_data["dealDetails"][j]

            drink_category = DRINK_CATEGORY[BEER]
            if deal_detail_data["category"] == "wine":
                drink_category = DRINK_CATEGORY[WINE]
            elif deal_detail_data["category"] == "liquor":
                drink_category = DRINK_CATEGORY[LIQUOR]

            deal_detail_type = DEAL_DETAIL_TYPE[PRICE]
            if deal_detail_data["dealType"] == "percent-off":
                deal_detail_type = DEAL_DETAIL_TYPE[PERCENT_OFF]
            elif deal_detail_data["dealType"] == "price-off":
                deal_detail_type = DEAL_DETAIL_TYPE[PRICE_OFF]

            deal_detail = DealDetail(
                drinkName = "",
                drinkCategory = drink_category,
                detailType = deal_detail_type,
                value = deal_detail_data["dealValue"],
            )
            deal_detail.save()
            deal.dealDetails.add(deal_detail)

            # Add drink names submitted by all Turkers.
            # First response will be in deal_json, remaining will be ordered in matching_deals
            drink_name_option = MTurkDrinkNameOption(name = deal_detail_data["names"])
            drink_name_option.save()
            deal_detail.mturkDrinkNameOptions.add(drink_name_option)

            for matching_deal in matching_deals:
                drink_name_option = MTurkDrinkNameOption(name = matching_deal[i][j]["names"])
                drink_name_option.save()
                deal_detail.mturkDrinkNameOptions.add(drink_name_option)


# Combine names from same category/time deal details that are entered separately
# e.g. Heineken $4 MWF 4-7 PM and Budweiser $4 MWF 4-7 PM becomes Heineken, Budweiser $4 MWF 4-7PM
def combine_deal_detail_drink_names(deal_json):

    for i in range(len(deal_json["dealData"])):
        deal_details = deal_json["dealData"][i]["dealDetails"]

        match_index = 0
        while match_index < len(deal_details):

            matches = []
            match_candidate_index = match_index + 1
            while match_candidate_index < len(deal_details):
                if (deal_details_match(deal_details[match_index], deal_details[match_candidate_index])):
                    matches.append(deal_details.pop(match_candidate_index))

                match_candidate_index += 1

            if len(matches) > 0:
                for j in range(len(matches)):
                    match = matches[j]
                    deal_details[match_index]["names"] += ", " + match["names"]

            match_index += 1

    return deal_json


# Merge deal JSON data entered by multiple Turkers into a list of objects for each deal/deal detail combination:
# [
#    {
#        daysOfWeek:
#        timePeriods:
#        dealDetailOptions: [
#            {
#                names:
#                category:
#                dealType:
#                dealValue:
#            }, ...
#        ]
#    }, ...
def merge_deal_jsons(deal_jsons):
    for i in range(len(deal_jsons)):
        deal_jsons[i] = combine_deal_detail_drink_names(deal_jsons[1])

    results = []

    for i in range(len(deal_jsons)):
        deal_json = deal_jsons[i]

        for deal_data in deal_json["dealData"]:

            # If we have already considered this deal data, skip it
            if len(get_matching_time_frame_deals(results, deal_data)) > 0:
                continue

            # Otherwise, try to find matching deal data from all deal jsons after it
            matching_deals = []
            for deal_json in deal_jsons[i + 1:]:
                matching_deal_data_candidates = deal_json["dealData"]
                matches_for_deal_json = get_matching_time_frame_deals(matching_deal_data_candidates, deal_data)

                for match in matches_for_deal_json:
                    matching_deals.append(match)

            result = {
                "daysOfWeek": deal_data["daysOfWeek"],
                "timePeriods": deal_data["timePeriods"],
                "dealDetailOptions": deal_data["dealDetails"]
            }

            for matching_deal in matching_deals:
                for deal_detail in matching_deal["dealDetails"]:
                    result["dealDetailOptions"].append(deal_detail)

            results.append(result)

    return results


# Helper method to retrieve all instances matching the time frame of deal_to_find in deal_detail_array
# Returns matching index in deal_data_array if match is found, otherwise returns None
def get_matching_time_frame_deals(deal_data_array, deal_to_find):

    matching_deals = []

    for deal_data in deal_data_array:

        if (len(deal_data["daysOfWeek"]) != len(deal_to_find["daysOfWeek"])):
            continue

        for j in range(0, len(deal_to_find["daysOfWeek"])):
            if deal_data["daysOfWeek"][j] != deal_to_find["daysOfWeek"][j]:
                continue

        if (len(deal_data["timePeriods"]) != len(deal_to_find["timePeriods"])):
            continue

        if len(deal_to_find["timePeriods"]) == 1:
            if (deal_to_find["timePeriods"][0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) or \
                (deal_to_find["timePeriods"][0]["endTime"] != deal_data["timePeriods"][0]["endTime"]):
                continue

        else: # length = 2
            if (deal_to_find["timePeriods"][0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) and \
                (deal_to_find["timePeriods"][0]["startTime"] != deal_data["timePeriods"][1]["startTime"]):
                continue

            if (deal_to_find["timePeriods"][1]["endTime"] != deal_data["timePeriods"][0]["endTime"]) and \
                (deal_to_find["timePeriods"][1]["endTime"] != deal_data["timePeriods"][1]["endTime"]):
                continue

        # Add match
        matching_deals.append(deal_data)

    return matching_deals


# def get_match_percentages(deal_jsons):
#     # Standardize by combining matching deal details from within responses
#     for i in range(len(deal_jsons)):
#         deal_jsons[i] = combine_deal_details(deal_jsons[i])
#
#     max_match_percentage = 0.0
#     max_matches_deal_json = None
#     max_matches_matching_deals = None
#
#     for i in range(0, len(deal_jsons)):
#
#         current_deal_json = deal_jsons[i]
#         current_matching_deals = []
#
#         for j in range(0, len(deal_jsons)):
#             if i != j:
#                 matching_deals = deals_responses_match(current_deal_json, deal_jsons[j])
#
#                 if matching_deals != None:
#                     current_matching_deals.append(matching_deals)
#
#         match_percentage = float(len(current_matching_deals) + 1) / float(len(deal_jsons))
#
#         if match_percentage > max_match_percentage:
#             max_match_percentage = match_percentage
#             max_matches_deal_json = current_deal_json
#             max_matches_matching_deals = current_matching_deals
#
#     return (max_match_percentage, max_matches_deal_json, max_matches_matching_deals)


# Check to see if two sets of deals from two different Turkers match.
# Matching requires that for every deal detail, the price, deal type and drink category are the same
# And the time ranges match up as well.
# def deals_responses_match(deal_json_a, deal_json_b):
#     matching_deal_responses = []
#
#     if len(deal_json_a["dealData"]) == len(deal_json_b["dealData"]):
#
#         for deal_data in deal_json_a["dealData"]:
#             deal_details_b = get_deal_details_for_time_frame(deal_data["daysOfWeek"], deal_data["timePeriods"], deal_json_b)
#
#             if deal_details_b != None:
#                 matches = deal_details_set_match(deal_data["dealDetails"], deal_details_b)
#
#                 if matches != None:
#                     matching_deal_responses.append(matches)
#
#     if len(matching_deal_responses) == len(deal_json_a["dealData"]):
#         return matching_deal_responses
#
#     return None


# Retrieve the deal details that match a certain days of week/time frame combination
# def get_deal_details_for_time_frame(days_of_week, time_periods, deal_json):
#
#     for deal_data in deal_json["dealData"]:
#
#         if len(deal_data["daysOfWeek"]) != len(days_of_week):
#             continue
#
#         for i in range(0, len(days_of_week)):
#             if (deal_data["daysOfWeek"][i] != days_of_week[i]):
#                 continue
#
#         if len(deal_data["timePeriods"]) != len(time_periods):
#             continue
#
#         if len(time_periods) == 1:
#             if (time_periods[0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) or \
#                 (time_periods[0]["endTime"] != deal_data["timePeriods"][0]["endTime"]):
#                 continue
#
#         else: # length = 2
#             if (time_periods[0]["startTime"] != deal_data["timePeriods"][0]["startTime"]) and \
#                 (time_periods[0]["startTime"] != deal_data["timePeriods"][1]["startTime"]):
#                 continue
#
#             if (time_periods[1]["endTime"] != deal_data["timePeriods"][0]["endTime"]) and \
#                 (time_periods[1]["endTime"] != deal_data["timePeriods"][1]["endTime"]):
#                 continue
#
#         return deal_data["dealDetails"]
#
#     return None


# If deal details set from A completely matches deal details set from B,
# return the deal details from B in order corresponding to those from A
# def deal_details_set_match(deal_details_a, deal_details_b):
#     matches = []
#
#     if (len(deal_details_a) == len(deal_details_b)):
#         for deal_detail in deal_details_a:
#             for match_candidate in deal_details_b:
#                 if (deal_details_match(deal_detail, match_candidate)):
#                     # Match found - save it
#                     matches.append(match_candidate)
#
#     if len(matches) == len(deal_details_a):
#         return matches
#
#     return None


def deal_details_match(deal_detail_a, deal_detail_b):
    return deal_detail_a["category"] == deal_detail_b["category"] and \
        deal_detail_a["dealType"] == deal_detail_b["dealType"] and \
        deal_detail_a["dealValue"] == deal_detail_b["dealValue"]
