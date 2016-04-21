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

    location = None
    location_info = None
    conn = None

    def handle(self, *args, **options):
        self.conn = connection.MTurkConnection(
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY,
            host = settings.MTURK_HOST
        )

        self.location = Location.objects.create(
            name = "Liberty Lounge TEST",
            formattedAddress = "3257 Stanton Rd SE,\nWashington, DC 20020",
            website = "http://www.justinhinh.com",
            formattedPhoneNumber = "(202)790-4414",
            mturkDateLastUpdated = timezone.now()
        )

        self.location_info = MTurkLocationInfo.objects.create(
            location = self.location,
            name = self.location.name,
            address = self.location.formattedAddress,
            phone_number = self.location.formattedPhoneNumber,
            website = self.location.website,
            stage = 0
        )

        mturk_utilities.register_hit_types(self.conn)

        if (args[1] == "0"):
           self.test_stage_0()
        elif (args[1] == "1"):
            self.test_stage_1()
        elif (args[1] == "2"):
            self.test_stage_2()
        elif (args[1] == "3"):
            self.test_stage_3()
        elif (args[1] == "4"):
            self.test_stage_4()
        elif (args[1] == "5"):
            self.test_stage_5()
        elif (args[1] == "6"):
            self.test_stage_6()

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


    # Stage 0: Find URL HIT
    def test_stage_0(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, FIND_WEBSITE)
        mturk_location.website = None
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 1: Find web happy hour
    def test_stage_1(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, FIND_HAPPY_HOUR_WEB)
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 2: Confirm web happy hour
    def test_stage_2(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_WEB)
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 3: Confirm web happy hour 2
    def test_stage_3(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_WEB_2)
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB_2])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        update_mturk_tasks.update()
        print("Updated")
        self.print_status()


    # Stage 4: Find phone happy hour
    def test_stage_4(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, FIND_HAPPY_HOUR_PHONE)
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_phone_tasks.update()
        print("Updated")
        self.print_status()


    #Stage 5: Confirm phone happy hour
    def test_stage_5(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_PHONE)
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_phone_tasks.update()
        print("Updated")
        self.print_status()

    #Stage 6: Confirm phone happy hour 2
    def test_stage_6(self):
        mturk_location = self.location_info
        mturk_utilities.add_mturk_stat(mturk_location, CONFIRM_HAPPY_HOUR_PHONE_2)
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE_2]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE_2])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_phone_tasks.update()
        print("Updated")
        self.print_status()