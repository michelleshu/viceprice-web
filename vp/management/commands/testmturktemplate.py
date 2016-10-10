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

    # def handle(self, *args, **options):
    #     update_mturk_tasks.update()

    def handle(self, *args, **options):
        conn = connection.MTurkConnection(
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY,
            host = settings.MTURK_HOST
        )

        location = Location.objects.create(
            name = "Liberty Lounge TEST",
            website = "http://www.justinhinh.com",
            formattedPhoneNumber = "(202)790-4414",
            dateLastUpdated = timezone.now()
        )

        mturk_location_info = MTurkLocationInfo.objects.create(
            location = location,
            name = location.name,
            phone_number = location.formattedPhoneNumber,
            website = location.website
        )

        mturk_location_info.save()

        mturk_utilities.register_hit_types(conn)
        mturk_utilities.create_hit(conn, mturk_location_info, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR])

        print("HIT " + mturk_location_info.hit_id + " created.")
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")

        mturk_location_info.delete()
        location.delete()