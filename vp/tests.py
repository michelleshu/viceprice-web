import datetime
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from models import Location, MTurkLocationInfo, BusinessHour
from mturk import mturk_utilities, mturk_update_website_tasks, mturk_update_phone_tasks
from boto.mturk import connection
from mock import MagicMock, mock
from pprint import pprint
from viceprice.constants import *

# TO RUN A SPECIFIC TEST:
# foreman run python manage.py test vp.tests.Test.test_function

# MTurk Tests

# Mock of boto.mturk.connection.Assignment.Answer
class MockAnswer():
    def __init__(self, qid, answer):
        self.qid = qid
        self.fields = [ answer ]

# Mock of boto.mturk.connection.Assignment
class MockAssignment():
    def __init__ (self, assignment_id = None):
        self.AssignmentId = assignment_id
        self.AssignmentStatus = SUBMITTED
        self.answers = [[]]

    def add_answer(self, qid, answer):
        self.answers[0].append(MockAnswer(qid, answer))

# Test retrieval of and initialization of locations that need updating
# We will have 3 locations that need updating, 2 that don't, and 2 others that are already in progress of being updated.
# First, we will set the max update constraint to 4 at a time. The code should pull only 2 additional locations that
# need updating.
# Then, we won't pass a max constraint, using the app default instead, in which case all 3 locations should be pulled
class AddLocationsToUpdateTest(TestCase):

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    expired_date = timezone.now() - datetime.timedelta(days = EXPIRATION_PERIOD + 1)
    unexpired_date = timezone.now()

    def setUp(self):
        location1 = Location.objects.create(name = "No Update Needed", mturkLastUpdateCompleted = self.unexpired_date)
        location2 = Location.objects.create(
            name = "Needs Update Stage 1",
            formattedAddress = "Address",
            formattedPhoneNumber = "Phone Number",
            website = "Website",
            mturkLastUpdateCompleted = self.expired_date
        )
        location3 = Location.objects.create(name = "No Update Needed", mturkLastUpdateCompleted = self.unexpired_date)
        location4 = Location.objects.create(name = "No Update Needed", mturkLastUpdateCompleted = self.unexpired_date)
        location5 = Location.objects.create(
            name = "Needs Update Stage 0",
            formattedAddress = "Address",
            formattedPhoneNumber = "Phone Number",
            mturkLastUpdateCompleted = self.expired_date
        )
        location6 = Location.objects.create(name = "No Update Needed", mturkLastUpdateCompleted = self.unexpired_date)
        location7 = Location.objects.create(
            name = "Needs Update Stage 1",
            formattedAddress = "Address",
            formattedPhoneNumber = "Phone Number",
            website = "Website",
            mturkLastUpdateCompleted = self.expired_date
        )

        MTurkLocationInfo.objects.create(name = "No Update Needed", location = location3, stage = MTURK_STAGE[FIND_WEBSITE])
        MTurkLocationInfo.objects.create(name = "No Update Needed", location = location6, stage = MTURK_STAGE[FIND_WEBSITE])
        # This one should not count since it is in no info found stage
        MTurkLocationInfo.objects.create(name = "No Update Needed", location = location5, stage = MTURK_STAGE[NO_INFO])

        mturk_utilities.register_hit_types(self.conn)

    # Test adding locations with a max constraint of 4
    def test_add_locations_to_update_with_constraint(self):
        mturk_utilities.add_mturk_locations_to_update(self.conn, max_to_add = 4)
        mturk_location_infos_added = list(MTurkLocationInfo.objects.filter(name__startswith = "Needs Update"))
        self.assertEqual(len(mturk_location_infos_added), 2)

        for location_info in mturk_location_infos_added:
            self.assertEqual(location_info.address, "Address")
            self.assertEqual(location_info.phone_number, "Phone Number")

            if (location_info.name == "Needs Update Stage 0"):
                self.assertEqual(location_info.stage, 0)
            elif (location_info.name == "Needs Update Stage 1"):
                self.assertEqual(location_info.website, "Website")
                self.assertEqual(location_info.stage, 1)

    # Test adding locations with the default max constraint specified in settings
    def test_add_locations_to_update(self):
        mturk_utilities.add_mturk_locations_to_update(self.conn)
        mturk_location_infos_added = list(MTurkLocationInfo.objects.filter(name__startswith = "Needs Update"))
        self.assertEqual(len(mturk_location_infos_added), 3)

        for location_info in mturk_location_infos_added:
            self.assertEqual(location_info.address, "Address")
            self.assertEqual(location_info.phone_number, "Phone Number")

            if (location_info.name == "Needs Update Stage 0"):
                self.assertEqual(location_info.stage, 0)
            elif (location_info.name == "Needs Update Stage 1"):
                self.assertEqual(location_info.website, "Website")
                self.assertEqual(location_info.stage, 1)


# Test retrieval of MTurkLocationInfo that are in progress
class GetLocationInfoTest(TestCase):

    def setUp(self):
        location1 = Location.objects.create(name = "Website Update")
        location2 = Location.objects.create(name = "Website Update")
        location3 = Location.objects.create(name = "Website Update")
        location4 = Location.objects.create(name = "Phone Update")
        location5 = Location.objects.create(name = "Phone Update")
        location6 = Location.objects.create(name = "Complete")
        location7 = Location.objects.create(name = "No Info")

        MTurkLocationInfo.objects.create(name = "Website Update", location = location1, stage = MTURK_STAGE[FIND_WEBSITE])
        MTurkLocationInfo.objects.create(name = "Website Update", location = location2, stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB])
        MTurkLocationInfo.objects.create(name = "Website Update", location = location3, stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB])
        MTurkLocationInfo.objects.create(name = "Phone Update", location = location4, stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE])
        MTurkLocationInfo.objects.create(name = "Phone Update", location = location5, stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE])
        MTurkLocationInfo.objects.create(name = "Complete", location = location6, stage = MTURK_STAGE[COMPLETE])
        MTurkLocationInfo.objects.create(name = "No Info", location = location7, stage = MTURK_STAGE[NO_INFO])

    # Test getting locations that are in a website update stage
    def test_get_website_update_mturk_locations(self):
        website_update_mturk_locations = mturk_utilities.get_website_update_mturk_locations()
        self.assertEqual(len(website_update_mturk_locations), 3)

        for location_info in website_update_mturk_locations:
            self.assertEqual(location_info.name, "Website Update")

    # Test getting locations that are in a phone update stage
    def test_get_phone_update_mturk_locations(self):
        phone_update_mturk_locations = mturk_utilities.get_phone_update_mturk_locations()
        self.assertEqual(len(phone_update_mturk_locations), 2)

        for location_info in phone_update_mturk_locations:
            self.assertEqual(location_info.name, "Phone Update")

    # Test getting locations that are complete
    def test_get_complete_mturk_locations(self):
        complete_mturk_locations = mturk_utilities.get_complete_mturk_locations()
        self.assertEqual(len(complete_mturk_locations), 1)

        for location_info in complete_mturk_locations:
            self.assertEqual(location_info.name, "Complete")

    # Test getting locations that we failed to get happy hour info for
    def test_get_no_info_mturk_locations(self):
        no_info_mturk_locations = mturk_utilities.get_no_info_mturk_locations()
        self.assertEqual(len(no_info_mturk_locations), 1)

        for location_info in no_info_mturk_locations:
            self.assertEqual(location_info.name, "No Info")


# Test creation of HIT layouts
# Manually check the layout appearance on development sandbox
# Then the HITs on Amazon can be deleted using the management command disablehits
class HITCreationTest(TestCase):

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    def setUp(self):
        location = Location.objects.create(
            name = "Liberty Lounge",
            formattedAddress = "3257 Stanton Rd SE,\nWashington, DC 20020",
            website = "http://www.justinhinh.com",
            formattedPhoneNumber = "(202)790-4414"
        )

        MTurkLocationInfo.objects.create(
            location = location,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            website = location.website,
            stage = 0
        )

        mturk_utilities.register_hit_types(self.conn)

    # Stage 0: Find URL HIT
    def test_stage_0(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])

    def test_stage_1(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])

    def test_stage_2(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB])

    def test_stage_3(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_WEB_2]
        mturk_location.deals = "***1|||17:00|||19:00|||Monday Description***2|||16:00|||19:00|||Tuesday Description" + \
            "***3|||17:00|||20:00|||Wednesday Description***4|||20:00|||22:00|||Thursday Description" + \
            "***5|||16:00|||19:00|||Friday Description***6|||17:00|||19:00|||Saturday Description" + \
            "***7|||18:00|||20:00|||Sunday Description"
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_WEB_2])

    def test_stage_4(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_PHONE]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_PHONE])

    def test_stage_5(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_location.stage = MTURK_STAGE[CONFIRM_HAPPY_HOUR_PHONE]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[CONFIRM_HAPPY_HOUR_PHONE])


# Test evaluation and update of completed HIT assignments
class HITUpdateTest(TestCase):

    conn = connection.MTurkConnection(
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        host = settings.MTURK_HOST)

    def setUp(self):
        location = Location.objects.create(
            name = "Liberty Lounge",
            formattedAddress = "3257 Stanton Rd SE,\nWashington, DC 20020",
            website = "http://www.justinhinh.com",
            formattedPhoneNumber = "(202)790-4414",
            mturkDateLastUpdated = timezone.now()
        )

        MTurkLocationInfo.objects.create(
            location = location,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            website = location.website,
            stage = 0
        )

        mturk_utilities.register_hit_types(self.conn)

    def print_status(self):
        mturk_locations = MTurkLocationInfo.objects.all()
        for mturk_location in mturk_locations:
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
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_utilities.add_mturk_stat(mturk_location, FIND_WEBSITE)
        mturk_location.website = None
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_website_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 1: Find web happy hour
    def test_stage_1(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_utilities.add_mturk_stat(mturk_location, FIND_HAPPY_HOUR_WEB)
        mturk_location.stage = MTURK_STAGE[FIND_HAPPY_HOUR_WEB]
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])

        print("HIT " + mturk_location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_website_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 2: Confirm web happy hour
    def test_stage_2(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
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

        mturk_update_website_tasks.update()
        print("Updated")
        self.print_status()

    # Stage 3: Confirm web happy hour 2
    def test_stage_3(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
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

        mturk_update_website_tasks.update()
        print("Updated")
        self.print_status()


    # Stage 4: Find phone happy hour
    def test_stage_4(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
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
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
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
        mturk_location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
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


# Test ProcessFindWebsite for Stage 0: Find URL of MTurk
class ProcessFindWebsiteTest(TestCase):
    def setUp(self):
        location = Location.objects.create(name = "FindURL")
        MTurkLocationInfo.objects.create(location = location, name = "FindURL", stage = 0, hit_id = "HIT_Id")

    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_agreement(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(WEBSITE_FOUND, 'yes')
        assignment1.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignment2 = MockAssignment()
        assignment2.add_answer(WEBSITE_FOUND, 'yes')
        assignment2.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignment3 = MockAssignment()
        assignment3.add_answer(WEBSITE_FOUND, 'yes')
        assignment3.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignments = [ assignment1, assignment2, assignment3 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mturk_location, assignments)

        self.assertEqual(result[0], 100.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_disagreement(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(WEBSITE_FOUND, 'yes')
        assignment1.add_answer(WEBSITE, 'http://www.libertylounge2.com')

        assignment2 = MockAssignment()
        assignment2.add_answer(WEBSITE_FOUND, 'yes')
        assignment2.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignment3 = MockAssignment()
        assignment3.add_answer(WEBSITE_FOUND, 'yes')
        assignment3.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignment4 = MockAssignment()
        assignment4.add_answer(WEBSITE_FOUND, 'yes')
        assignment4.add_answer(WEBSITE, 'http://www.libertylounge2.com')

        assignment5 = MockAssignment()
        assignment5.add_answer(WEBSITE_FOUND, 'yes')
        assignment5.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignments = [ assignment1, assignment2, assignment3, assignment4, assignment5 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mturk_location, assignments)

        self.assertEqual(result[0], 60.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_disagreement_no_url(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(WEBSITE_FOUND, 'no')
        assignment1.add_answer(WEBSITE, None)

        assignment2 = MockAssignment()
        assignment2.add_answer(WEBSITE_FOUND, 'yes')
        assignment2.add_answer(WEBSITE, 'http://www.libertylounge.com')

        assignment3 = MockAssignment()
        assignment3.add_answer(WEBSITE_FOUND, 'no')
        assignment3.add_answer(WEBSITE, None)

        assignment4 = MockAssignment()
        assignment4.add_answer(WEBSITE_FOUND, 'no')
        assignment4.add_answer(WEBSITE, None)

        assignments = [ assignment1, assignment2, assignment3, assignment4 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mturk_location, assignments)

        self.assertEqual(result[0], 75.0)
        self.assertEqual(result[1], None)


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_different_url_formats(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(WEBSITE_FOUND, 'yes')
        assignment1.add_answer(WEBSITE, 'www.libertylounge.com')

        assignment2 = MockAssignment()
        assignment2.add_answer(WEBSITE_FOUND, 'yes')
        assignment2.add_answer(WEBSITE, 'http://www.libertylounge.com/')

        assignment3 = MockAssignment()
        assignment3.add_answer(WEBSITE_FOUND, 'yes')
        assignment3.add_answer(WEBSITE, 'libertylounge.com/')

        assignment4 = MockAssignment()
        assignment4.add_answer(WEBSITE_FOUND, 'yes')
        assignment4.add_answer(WEBSITE, 'https://libertylounge.com')

        assignment5 = MockAssignment()
        assignment5.add_answer(WEBSITE_FOUND, 'yes')
        assignment5.add_answer(WEBSITE, 'www.libertylounge.net')

        assignments = [ assignment1, assignment2, assignment3, assignment4, assignment5 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mturk_location, assignments)

        self.assertEqual(result[0], 80.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


# Test GetHappyHourFound for Stage 1: Find Happy Hour Web
class GetHappyHourFoundTest(TestCase):
    def setUp(self):
        location = Location.objects.create(name = "GetHappyHour")
        MTurkLocationInfo.objects.create(location = location, name = "GetHappyHour", stage = 1, hit_id = "HIT_Id")

    def test_happy_hour_found(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "GetHappyHour")

        assignment = MockAssignment()
        assignment.add_answer(HAPPY_HOUR_FOUND, 'yes')

        result = mturk_utilities.get_happy_hour_found(mturk_location, assignment)

        self.assertTrue(result)

    def test_happy_hour_not_found(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "GetHappyHour")

        assignment = MockAssignment()
        assignment.add_answer(HAPPY_HOUR_FOUND, 'no')

        result = mturk_utilities.get_happy_hour_found(mturk_location, assignment)

        self.assertFalse(result)
        self.assertEqual(mturk_location.attempts, 1)

    def test_no_response(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "GetHappyHour")

        assignment = MockAssignment()
        assignment.add_answer(HAPPY_HOUR_FOUND, 'no-response')

        result = mturk_utilities.get_happy_hour_found(mturk_location, assignment)

        self.assertFalse(result)
        self.assertEqual(mturk_location.attempts, 1)

    def test_wrong_website(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "GetHappyHour")

        assignment = MockAssignment()
        assignment.add_answer(HAPPY_HOUR_FOUND, 'wrong-website')

        result = mturk_utilities.get_happy_hour_found(mturk_location, assignment)

        self.assertFalse(result)
        self.assertEqual(mturk_location.stage, MTURK_STAGE[WRONG_WEBSITE])

    def test_wrong_number(self):
        mturk_location = MTurkLocationInfo.objects.get(name = "GetHappyHour")

        assignment = MockAssignment()
        assignment.add_answer(HAPPY_HOUR_FOUND, 'wrong-phone-number')

        result = mturk_utilities.get_happy_hour_found(mturk_location, assignment)

        self.assertFalse(result)
        self.assertEqual(mturk_location.stage, MTURK_STAGE[WRONG_PHONE_NUMBER])


# Test that current time is within business hours
class WithinBusinessHoursTest(TestCase):
    def test_true(self):
        location = Location.objects.create(name = "BusinessHours")

        now = timezone.localtime(timezone.now())
        current_day = now.isoweekday()
        current_time = now.time()

        # Create business hours including now
        businessHour = BusinessHour.objects.create([{
            "start": (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) - datetime.timedelta(hours = 1)).time(),
            "end": (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) + datetime.timedelta(hours = 1)).time()
        }], [ current_day ])

        location.businessHours.add(businessHour)

        within_business_hours = mturk_utilities.within_business_hours(location.id)

        self.assertTrue(within_business_hours)

    def test_false(self):
        location = Location.objects.create(name = "BusinessHours")

        now = timezone.localtime(timezone.now())
        current_day = now.isoweekday()
        current_time = now.time()

        # Create business hours including now
        businessHour = BusinessHour.objects.create([{
            "start": (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) + datetime.timedelta(hours = 1)).time(),
            "end": (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) + datetime.timedelta(hours = 2)).time()
        }], [ current_day ])

        location.businessHours.add(businessHour)

        within_business_hours = mturk_utilities.within_business_hours(location.id)

        self.assertFalse(within_business_hours)