__author__ = 'michelleshu'

from mturk_utilities import *
import django
import string
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
                    confirmed_deals = get_confirmed_deals(deal_jsons)

                    # If able to match any deal details, save the HIT results
                    if len(deal_jsons) >= settings.MIN_RESPONSES and len(confirmed_deals) > 0:
                        comment_string = ("\n".join(comments))[:1000]
                        save_results(mturk_location.location, confirmed_deals, comment_string)

                        if mturk_location.stat != None:
                            complete_mturk_stat(mturk_location, True)
                        
                        approve_and_dispose(conn, hit)
                        mturk_location.location.dateLastUpdated = timezone.now()
                        mturk_location.location.save()
                        mturk_location.delete()

                    # Otherwise, if max number of assignments has not been reached, extend the HIT
                    elif len(assignments) < settings.MAX_ASSIGNMENTS_TO_PUBLISH:
                        extend(conn, hit, mturk_location)

                    else:
                        # Fail the HIT since we cannot exceed max number of assignments on Amazon
                        if mturk_location.stat != None:
                            complete_mturk_stat(mturk_location, False)

                        approve_and_dispose(conn, hit)
                        mturk_location.location.mturkDataCollectionFailed = True
                        mturk_location.location.dateLastUpdated = timezone.now()
                        mturk_location.location.save()
                        mturk_location.delete()

                else:
                    # Not enough people found data. Mark the HIT as no data
                    if mturk_location.stat != None:
                        complete_mturk_stat(mturk_location, False)

                    approve_and_dispose(conn, hit)
                    mturk_location.location.mturkNoDealData = True
                    mturk_location.location.dateLastUpdated = timezone.now()
                    mturk_location.location.save()
                    mturk_location.delete()


def save_results(location, deals_data, comments):

    for deal_data in deals_data:
        deal = Deal(
            comments = comments,
            confirmed = False
        )
        deal.save()

        location.deals.add(deal)
        location.save()

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

            # Add drink names options submitted by all Turkers
            for names_option in deal_detail_data["namesOptions"]:
                capitalized_name_option = string.capwords(names_option, " ")
                drink_name_option = MTurkDrinkNameOption(name = capitalized_name_option)
                drink_name_option.save()
                deal_detail.mturkDrinkNameOptions.add(drink_name_option)


# Combine names from same category/time deal details that are entered separately
# e.g. Heineken $4 MWF 4-7 PM and Budweiser $4 MWF 4-7 PM becomes Heineken, Budweiser $4 MWF 4-7PM
def combine_deal_detail_drink_names(deal_datas):

    for i in range(len(deal_datas)):
        deal_details = deal_datas[i]["dealDetails"]

        match_index = 0
        while match_index < len(deal_details):

            matches = []
            match_candidate_index = match_index + 1

            while match_candidate_index < len(deal_details):
                if (deal_details_match(deal_details[match_index], deal_details[match_candidate_index])):
                    matches.append(deal_details.pop(match_candidate_index))
                else:
                    match_candidate_index += 1

            if len(matches) > 0:
                for j in range(len(matches)):
                    match = matches[j]
                    deal_details[match_index]["names"] += ", " + match["names"]

            match_index += 1

    return deal_datas


# Get confirmed portions of deals (includes any individual deal detail for which there is enough agreement beyond Turkers)
def get_confirmed_deals(deal_jsons): 
    responses_count = len(deal_jsons)
    merged_deals = merge_deal_jsons(deal_jsons)

    confirmed_deals = []

    for deal in merged_deals:

        confirmed_deal = {
            "daysOfWeek": deal["daysOfWeek"],
            "timePeriods": deal["timePeriods"],
            "dealDetails": []
        }

        deal_detail_options = deal["dealDetailOptions"]

        for i in range(len(deal_detail_options)):

            matched_count = 1

            deal_detail = {
                "category": deal_detail_options[i]["category"],
                "dealType": deal_detail_options[i]["dealType"],
                "dealValue": deal_detail_options[i]["dealValue"],
                "namesOptions": [deal_detail_options[i]["names"]]
            }

            for j in range(i + 1, len(deal_detail_options)):
                if deal_details_match(deal_detail, deal_detail_options[j]):
                    deal_detail["namesOptions"].append(deal_detail_options[j]["names"])
                    matched_count += 1
            
            if (float(matched_count) / float(responses_count) * 100.0) >= settings.MIN_AGREEMENT_PERCENTAGE:
                confirmed_deal["dealDetails"].append(deal_detail)

        if len(confirmed_deal["dealDetails"]) > 0:
            confirmed_deals.append(confirmed_deal)
    
    return confirmed_deals


# Merge deal JSON data entered by multiple Turkers into a list of objects for each deal/deal detail combination in
# the following format:
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
    results = []

    for i in range(len(deal_jsons)):
        deal_json = deal_jsons[i]
        deal_datas = combine_deal_elements(deal_json["dealData"])
        deal_jsons[i] = combine_deal_detail_drink_names(deal_datas)
    
    for i in range(len(deal_jsons)):
        for deal_data in deal_jsons[i]:

            # If we have already considered this deal data, skip it
            if len(get_matching_time_frame_deals(results, deal_data)) > 0:
                continue

            # Otherwise, try to find matching deal data from all deal jsons after it
            matching_deals = []
            for deal_json in deal_jsons[i + 1:]:
                matching_deal_data_candidates = deal_json
                matches_for_deal_json = get_matching_time_frame_deals(matching_deal_data_candidates, deal_data)

                for match in matches_for_deal_json:
                    matching_deals.append(match)

            result = {
                "daysOfWeek": deal_data["daysOfWeek"],
                "timePeriods": deal_data["timePeriods"],
                "dealDetailOptions": deal_data["dealDetails"]
            }

            for matching_deal in matching_deals:

                for deal_detail_index in range(len(matching_deal["dealDetails"])):
                    deal_detail = matching_deal["dealDetails"][deal_detail_index]
                    result["dealDetailOptions"].append(deal_detail)

            results.append(result)
    
    return results

# Combine duplicate time frames entered by same person
def combine_deal_elements(dealData):
    result = []
    indices_to_ignore = []  # indices that have been merged 
    
    for i in range(len(dealData)):
        if (i not in indices_to_ignore):
            deal_details_to_merge = []
            
            for j in range(i + 1, len(dealData)):
                if (j not in indices_to_ignore):
                    match = get_matching_time_frame_deals([dealData[j]], dealData[i])
                    if (len(match) > 0):
                        deal_details_to_merge += dealData[j]["dealDetails"]
                        indices_to_ignore.append(j)
            
            dealData[i]["dealDetails"] += deal_details_to_merge
            result.append(dealData[i])
    
    return result
        
# Helper method to retrieve all instances matching the time frame of deal_to_find in deal_detail_array
# Returns matching index in deal_data_array if match is found, otherwise returns None
def get_matching_time_frame_deals(deal_data_array, deal_to_find):

    matching_deals = []

    for deal_data in deal_data_array:

        if (len(deal_data["daysOfWeek"]) != len(deal_to_find["daysOfWeek"])):
            continue

        days_of_week_match = True
        for j in range(0, len(deal_to_find["daysOfWeek"])):
            if deal_data["daysOfWeek"][j] != deal_to_find["daysOfWeek"][j]:
                days_of_week_match = False
                break
        
        if not days_of_week_match:
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


def deal_details_match(deal_detail_a, deal_detail_b):
    return deal_detail_a["category"] == deal_detail_b["category"] and \
        deal_detail_a["dealType"] == deal_detail_b["dealType"] and \
        deal_detail_a["dealValue"] == deal_detail_b["dealValue"]