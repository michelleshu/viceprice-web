import django
import django.utils.timezone
from viceprice.constants import *
from time import strptime
from vp.mturk import mturk_utilities
from vp.models import BusinessHour, Deal

django.setup()

# Helper functions to update db with MTurk data

def parse_deal(dealString):
    deal_properties = dealString.split("|||")
    day = int(deal_properties[0])
    deal_hour = BusinessHour.objects.create([
        {
            'start': deal_properties[1],
            'end': deal_properties[2]
        }],
        [ day ]
    )
    deal_hour.save()
    deal = Deal(dealHour = deal_hour, description = deal_properties[3])
    deal.save()
    return deal


def get_deals_for_location(mturk_location):
    dealStrings = mturk_location.deals.split("***")[1:]
    deals = []

    for dealString in dealStrings:
        deals.append(parse_deal(dealString))

    return deals


def write_mturk_deals_to_db():
    complete_locations = mturk_utilities.get_complete_mturk_locations()

    for mturk_location in complete_locations:

        if (mturk_location.deals != None and mturk_location.deals != ''):
            location = mturk_location.location
            location.name = mturk_location.name
            location.website = mturk_location.website
            location.comments = mturk_location.comments
            location.dateLastUpdated = django.utils.timezone.now()

            location.deals.all().delete()

            deals = get_deals_for_location(mturk_location)
            for deal in deals:
                location.deals.add(deal)

            mturk_location.delete()
            location.save()

        else:
            mturk_location.stage = MTURK_STAGE[NO_INFO]
            mturk_location.save()

