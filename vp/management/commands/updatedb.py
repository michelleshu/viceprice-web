from django.core.management.base import BaseCommand
import django.utils.timezone
from vp.mturk import mturk_utilities
from vp.models import *

class Command(BaseCommand):
    help = 'Updates database with Mechanical Turk data'
    args = '<site>'

    def get_deals_for_location(self, mturk_location):
        deals = []

        if mturk_location.monday_description != None and mturk_location.monday_description != '':
            monday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.monday_start_time.replace(":", ""),
                    'end': mturk_location.monday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[MONDAY]]
            )
            monday_deal_hour.save()
            monday_deal = Deal(dealHour = monday_deal_hour, description = mturk_location.monday_description.replace("&#10;", "\n"))
            monday_deal.save()
            deals.append(monday_deal)

        if mturk_location.tuesday_description != None and mturk_location.tuesday_description != '':
            tuesday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.tuesday_start_time.replace(":", ""),
                    'end': mturk_location.tuesday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[TUESDAY]]
            )
            tuesday_deal_hour.save()
            tuesday_deal = Deal(dealHour = tuesday_deal_hour, description = mturk_location.tuesday_description.replace("&#10;", "\n"))
            tuesday_deal.save()
            deals.append(tuesday_deal)

        if mturk_location.wednesday_description != None and mturk_location.wednesday_description != '':
            wednesday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.wednesday_start_time.replace(":", ""),
                    'end': mturk_location.wednesday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[WEDNESDAY]]
            )
            wednesday_deal_hour.save()
            wednesday_deal = Deal(dealHour = wednesday_deal_hour, description = mturk_location.wednesday_description.replace("&#10;", "\n"))
            wednesday_deal.save()
            deals.append(wednesday_deal)

        if mturk_location.thursday_description != None and mturk_location.thursday_description != '':
            thursday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.thursday_start_time.replace(":", ""),
                    'end': mturk_location.thursday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[THURSDAY]]
            )
            thursday_deal_hour.save()
            thursday_deal = Deal(dealHour = thursday_deal_hour, description = mturk_location.thursday_description.replace("&#10;", "\n"))
            thursday_deal.save()
            deals.append(thursday_deal)

        if mturk_location.friday_description != None and mturk_location.friday_description != '':
            friday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.friday_start_time.replace(":", ""),
                    'end': mturk_location.friday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[FRIDAY]]
            )
            friday_deal_hour.save()
            friday_deal = Deal(dealHour = friday_deal_hour, description = mturk_location.friday_description.replace("&#10;", "\n"))
            friday_deal.save()
            deals.append(friday_deal)

        if mturk_location.saturday_description != None and mturk_location.saturday_description != '':
            saturday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.saturday_start_time.replace(":", ""),
                    'end': mturk_location.saturday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[SATURDAY]]
            )
            saturday_deal_hour.save()
            saturday_deal = Deal(dealHour = saturday_deal_hour, description = mturk_location.saturday_description.replace("&#10;", "\n"))
            saturday_deal.save()
            deals.append(saturday_deal)

        if mturk_location.sunday_description != None and mturk_location.sunday_description != '':
            sunday_deal_hour = BusinessHour.objects.create([
                {
                    'start': mturk_location.sunday_start_time.replace(":", ""),
                    'end': mturk_location.sunday_end_time.replace(":", "")
                }],
                [DAY_OF_WEEK[SUNDAY]]
            )
            sunday_deal_hour.save()
            sunday_deal = Deal(dealHour = sunday_deal_hour, description = mturk_location.sunday_description.replace("&#10;", "\n"))
            sunday_deal.save()
            deals.append(sunday_deal)

        return deals


    def write_mturk_deals_to_db(self):
        updated_locations = mturk_utilities.get_all_updated_locations()

        for updated_location in updated_locations:
            mturk_location = updated_location[0]

            data_source_id = None
            if (updated_location[1] == 'web'):
                data_source_id = DEAL_DATA_SOURCE[MTURK_WEBSITE]
            elif (updated_location[1] == 'phone'):
                data_source_id = DEAL_DATA_SOURCE[MTURK_PHONE]
            elif (updated_location[1] == 'not_found'):
                data_source_id = DEAL_DATA_SOURCE[SOURCE_NOT_FOUND]

            location, created = Location.objects.get_or_create(foursquareId = mturk_location.foursquare_id)
            location.mturkDateLastUpdated = datetime.now()
            location.name = mturk_location.name
            location.formattedAddress = mturk_location.address
            location.latitude = float(mturk_location.latitude)
            location.longitude = float(mturk_location.longitude)
            location.formattedPhoneNumber = mturk_location.phone_number
            location.website = mturk_location.url

            if location.check_ins != None:
                location.check_ins = int(mturk_location.check_ins)

            if location.rating != None:
                location.rating = float(mturk_location.rating)

            location.comments = mturk_location.comments
            location.dateLastUpdated = django.utils.timezone.now()

            for deal in self.get_deals_for_location(mturk_location):
                location.deals.add(deal)

            if data_source_id != None:
                data_source = DealDataSource.objects.get(id = data_source_id)
                location.dealDataSource = data_source

            location.save()

    def handle(self, *args, **options):
        self.write_mturk_deals_to_db()