import django
import django.utils.timezone
from vp.mturk import mturk_utilities
from vp.models import Location, BusinessHour, \
    Deal, DAY_OF_WEEK, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY

django.setup()

# Helper functions to update db with MTurk data

def get_deals_for_location(mturk_location):
    deals = []

    if mturk_location.monday_description != None and mturk_location.monday_description != '' and mturk_location.monday_description != 'None':
        monday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.monday_start_time,
                'end': mturk_location.monday_end_time
            }],
            [DAY_OF_WEEK[MONDAY]]
        )
        monday_deal_hour.save()
        monday_deal = Deal(dealHour = monday_deal_hour, description = mturk_location.monday_description)
        monday_deal.save()
        deals.append(monday_deal)

    if mturk_location.tuesday_description != None and mturk_location.tuesday_description != '' and mturk_location.tuesday_description != 'None':
        tuesday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.tuesday_start_time,
                'end': mturk_location.tuesday_end_time
            }],
            [DAY_OF_WEEK[TUESDAY]]
        )
        tuesday_deal_hour.save()
        tuesday_deal = Deal(dealHour = tuesday_deal_hour, description = mturk_location.tuesday_description)
        tuesday_deal.save()
        deals.append(tuesday_deal)

    if mturk_location.wednesday_description != None and mturk_location.wednesday_description != '' and mturk_location.wednesday_description != 'None':
        wednesday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.wednesday_start_time,
                'end': mturk_location.wednesday_end_time
            }],
            [DAY_OF_WEEK[WEDNESDAY]]
        )
        wednesday_deal_hour.save()
        wednesday_deal = Deal(dealHour = wednesday_deal_hour, description = mturk_location.wednesday_description)
        wednesday_deal.save()
        deals.append(wednesday_deal)

    if mturk_location.thursday_description != None and mturk_location.thursday_description != '' and mturk_location.thursday_description != 'None':
        thursday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.thursday_start_time,
                'end': mturk_location.thursday_end_time
            }],
            [DAY_OF_WEEK[THURSDAY]]
        )
        thursday_deal_hour.save()
        thursday_deal = Deal(dealHour = thursday_deal_hour, description = mturk_location.thursday_description)
        thursday_deal.save()
        deals.append(thursday_deal)

    if mturk_location.friday_description != None and mturk_location.friday_description != '' and mturk_location.friday_description != 'None':
        friday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.friday_start_time,
                'end': mturk_location.friday_end_time
            }],
            [DAY_OF_WEEK[FRIDAY]]
        )
        friday_deal_hour.save()
        friday_deal = Deal(dealHour = friday_deal_hour, description = mturk_location.friday_description)
        friday_deal.save()
        deals.append(friday_deal)

    if mturk_location.saturday_description != None and mturk_location.saturday_description != '' and mturk_location.saturday_description != 'None':
        saturday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.saturday_start_time,
                'end': mturk_location.saturday_end_time
            }],
            [DAY_OF_WEEK[SATURDAY]]
        )
        saturday_deal_hour.save()
        saturday_deal = Deal(dealHour = saturday_deal_hour, description = mturk_location.saturday_description)
        saturday_deal.save()
        deals.append(saturday_deal)

    if mturk_location.sunday_description != None and mturk_location.sunday_description != '' and mturk_location.sunday_description != 'None':
        sunday_deal_hour = BusinessHour.objects.create([
            {
                'start': mturk_location.sunday_start_time,
                'end': mturk_location.sunday_end_time
            }],
            [DAY_OF_WEEK[SUNDAY]]
        )
        sunday_deal_hour.save()
        sunday_deal = Deal(dealHour = sunday_deal_hour, description = mturk_location.sunday_description)
        sunday_deal.save()
        deals.append(sunday_deal)

    return deals


def write_mturk_deals_to_db():
    complete_locations = mturk_utilities.get_complete_locations()

    for mturk_location in complete_locations:
        location, created = Location.objects.get_or_create(foursquareId = mturk_location.foursquare_id)
        location.mturkLastUpdateStarted = mturk_location.update_started
        location.mturkLastUpdateCompleted = mturk_location.update_completed
        location.mturkLastUpdateCost = mturk_location.update_cost
        location.name = mturk_location.name
        location.formattedAddress = mturk_location.address
        location.formattedPhoneNumber = mturk_location.phone_number
        location.website = mturk_location.url
        location.dealDataSource = mturk_location.data_source

        location.comments = mturk_location.comments
        location.dateLastUpdated = django.utils.timezone.now()

        deals = get_deals_for_location(mturk_location)

        for deal in deals:
            location.deals.add(deal)

        if len(deals) == 0:
            location.stage = mturk_utilities.MTURK_STAGE[mturk_utilities.NO_HH_FOUND]
        else:
            mturk_location.delete()

        location.save()