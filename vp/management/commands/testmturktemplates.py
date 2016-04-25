from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from boto.mturk import connection
from vp.models import Location, MTurkLocationInfo
from vp.mturk import mturk_utilities, mturk_update_phone_tasks, update_mturk_tasks
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
            location = self.location,
            name = self.location.name,
            address = self.location.formattedAddress,
            phone_number = self.location.formattedPhoneNumber,
            website = self.location.website,
            stage = 0
        )

        #mturk_utilities.register_hit_types(self.conn)

        mturk_utilities.add_mturk_stat(mturk_location_info, FIND_HAPPY_HOUR_WEB)
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status()

        self.location_info.delete()
        self.location.delete()


    def print_status(self):
        mturk_location = self.location_info

        print(mturk_location.name)

        if mturk_location.stage != None:
            print('  Stage: ' + str(mturk_location.stage))
        if mturk_location.website != None:
            print('  Website: ' + mturk_location.website)
        if mturk_location.hit_id != None:
            print('  HIT ID: ' + str(mturk_location.hit_id))
        if mturk_location.deals != None:
            print('  Deals: ' + mturk_location.deals)
        if mturk_location.attempts != None:
            print('  Attempts: ' + str(mturk_location.attempts))
        if mturk_location.confirmations != None:
            print('  Confirmations: ' + str(mturk_location.confirmations))
        if mturk_location.comments != None:
            print('  Comments: ' + mturk_location.comments)