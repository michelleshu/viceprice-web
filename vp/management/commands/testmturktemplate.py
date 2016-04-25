from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from boto.mturk import connection
from vp.models import Location, MTurkLocationInfo
from vp.mturk import mturk_utilities, update_mturk_tasks
from viceprice.constants import *

class Command(BaseCommand):
    help = 'Create MTurk HIT for test'
    args ='<site> <stage>'

    def handle(self, *args, **options):
        conn = connection.MTurkConnection(
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY,
            host = settings.MTURK_HOST
        )

        location = Location.objects.create(
            name = "Liberty Lounge TEST",
            formattedAddress = "3257 Stanton Rd SE,\nWashington, DC 20020",
            website = "http://www.justinhinh.com",
            formattedPhoneNumber = "(202)790-4414",
            mturkDateLastUpdated = timezone.now()
        )

        mturk_location_info = MTurkLocationInfo.objects.create(
            location = location,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            website = location.website
        )

        mturk_location_info.save()

        mturk_utilities.register_hit_types(conn)
        mturk_utilities.create_hit(conn, mturk_location_info, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR])

        print("HIT " + mturk_location_info.hit_id + " created.")
        self.print_status(mturk_location_info)
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status(mturk_location_info)

        mturk_location_info.delete()
        location.delete()


    def print_status(self, mturk_location_info):
        print(mturk_location_info.name)

        if mturk_location_info.website != None:
            print('  Website: ' + mturk_location_info.website)
        if mturk_location_info.hit_id != None:
            print('  HIT ID: ' + str(mturk_location_info.hit_id))
        if mturk_location_info.deals != None:
            print('  Deals: ' + mturk_location_info.deals)
        if mturk_location_info.attempts != None:
            print('  Attempts: ' + str(mturk_location_info.attempts))
        if mturk_location_info.confirmations != None:
            print('  Confirmations: ' + str(mturk_location_info.confirmations))
        if mturk_location_info.comments != None:
            print('  Comments: ' + mturk_location_info.comments)