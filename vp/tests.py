import datetime
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from models import Location, MTurkLocationInfo
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
        mturk_location.stage = 1
        mturk_location.save()
        mturk_utilities.create_hit(self.conn, mturk_location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])


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
            formattedPhoneNumber = "(202)790-4414"
        )

        MTurkLocationInfo.objects.create(
            location = location,
            name = location.name,
            address = location.formattedAddress,
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
                print('  Website: ' + str(mturk_location.website))
            if mturk_location.hit_id != None:
                print('  HIT ID: ' + str(mturk_location.hit_id))

    # Stage 0: Find URL HIT
    def test_stage_0(self):
        location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        location.website = None
        location.save()
        mturk_utilities.create_hit(self.conn, location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])

        print("HIT " + location.hit_id + " created.")
        self.print_status()
        raw_input("Respond at workersandbox.mturk.com...")

        mturk_update_website_tasks.update()
        print("Updated")
        self.print_status()

    def test_stage_1(self):
        location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        location.stage = 1
        location.save()
        mturk_utilities.create_hit(self.conn, location, settings.MTURK_HIT_TYPES[FIND_HAPPY_HOUR_WEB])


# Test Stage 0: Find URL of MTurk
class ProcessFindWebsiteTest(TestCase):
    def setUp(self):
        location = Location.objects.create(name = "FindURL")
        MTurkLocationInfo.objects.create(location = location, name = "FindURL", stage = 0, hit_id = "HIT_Id")

    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_agreement(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(URL_FOUND, 'yes')
        assignment1.add_answer(URL, 'http://www.libertylounge.com')
        assignment1.add_answer(ATTENTION_CHECK, 'correct')

        assignment2 = MockAssignment()
        assignment2.add_answer(URL_FOUND, 'yes')
        assignment2.add_answer(URL, 'http://www.libertylounge.com')
        assignment2.add_answer(ATTENTION_CHECK, 'correct')

        assignment3 = MockAssignment()
        assignment3.add_answer(URL_FOUND, 'yes')
        assignment3.add_answer(URL, 'http://www.libertylounge.com')
        assignment3.add_answer(ATTENTION_CHECK, 'correct')

        assignments = [ assignment1, assignment2, assignment3 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mock_connection, mturk_location, assignments)

        self.assertEqual(result[0], 100.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_disagreement(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(URL_FOUND, 'yes')
        assignment1.add_answer(URL, 'http://www.libertylounge2.com')
        assignment1.add_answer(ATTENTION_CHECK, 'correct')

        assignment2 = MockAssignment()
        assignment2.add_answer(URL_FOUND, 'yes')
        assignment2.add_answer(URL, 'http://www.libertylounge.com')
        assignment2.add_answer(ATTENTION_CHECK, 'correct')

        assignment3 = MockAssignment()
        assignment3.add_answer(URL_FOUND, 'yes')
        assignment3.add_answer(URL, 'http://www.libertylounge.com')
        assignment3.add_answer(ATTENTION_CHECK, 'correct')

        assignment4 = MockAssignment()
        assignment4.add_answer(URL_FOUND, 'yes')
        assignment4.add_answer(URL, 'http://www.libertylounge2.com')
        assignment4.add_answer(ATTENTION_CHECK, 'correct')

        assignment5 = MockAssignment()
        assignment5.add_answer(URL_FOUND, 'yes')
        assignment5.add_answer(URL, 'http://www.libertylounge.com')
        assignment5.add_answer(ATTENTION_CHECK, 'correct')

        assignments = [ assignment1, assignment2, assignment3, assignment4, assignment5 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mock_connection, mturk_location, assignments)

        self.assertEqual(result[0], 60.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_disagreement_no_url(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(URL_FOUND, 'no')
        assignment1.add_answer(URL, None)
        assignment1.add_answer(ATTENTION_CHECK, 'correct')

        assignment2 = MockAssignment()
        assignment2.add_answer(URL_FOUND, 'yes')
        assignment2.add_answer(URL, 'http://www.libertylounge.com')
        assignment2.add_answer(ATTENTION_CHECK, 'correct')

        assignment3 = MockAssignment()
        assignment3.add_answer(URL_FOUND, 'no')
        assignment3.add_answer(URL, None)
        assignment3.add_answer(ATTENTION_CHECK, 'correct')

        assignment4 = MockAssignment()
        assignment4.add_answer(URL_FOUND, 'no')
        assignment4.add_answer(URL, None)
        assignment4.add_answer(ATTENTION_CHECK, 'correct')

        assignments = [ assignment1, assignment2, assignment3, assignment4 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mock_connection, mturk_location, assignments)

        self.assertEqual(result[0], 75.0)
        self.assertEqual(result[1], None)


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_different_url_formats(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment()
        assignment1.add_answer(URL_FOUND, 'yes')
        assignment1.add_answer(URL, 'www.libertylounge.com')
        assignment1.add_answer(ATTENTION_CHECK, 'correct')

        assignment2 = MockAssignment()
        assignment2.add_answer(URL_FOUND, 'yes')
        assignment2.add_answer(URL, 'http://www.libertylounge.com/')
        assignment2.add_answer(ATTENTION_CHECK, 'correct')

        assignment3 = MockAssignment()
        assignment3.add_answer(URL_FOUND, 'yes')
        assignment3.add_answer(URL, 'libertylounge.com/')
        assignment3.add_answer(ATTENTION_CHECK, 'correct')

        assignment4 = MockAssignment()
        assignment4.add_answer(URL_FOUND, 'yes')
        assignment4.add_answer(URL, 'https://libertylounge.com')
        assignment4.add_answer(ATTENTION_CHECK, 'correct')

        assignment5 = MockAssignment()
        assignment5.add_answer(URL_FOUND, 'yes')
        assignment5.add_answer(URL, 'www.libertylounge.net')
        assignment5.add_answer(ATTENTION_CHECK, 'correct')

        assignments = [ assignment1, assignment2, assignment3, assignment4, assignment5 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mock_connection, mturk_location, assignments)

        self.assertEqual(result[0], 80.0)
        self.assertEqual(result[1], 'http://www.libertylounge.com')


    @mock.patch('boto.mturk.connection.MTurkConnection')
    def test_fail_attention_check(self, mock_connection):
        mturk_location = MTurkLocationInfo.objects.get(name = "FindURL")

        assignment1 = MockAssignment(assignment_id = 1)
        assignment1.add_answer(URL_FOUND, 'yes')
        assignment1.add_answer(URL, 'http://www.libertylounge.com')
        assignment1.add_answer(ATTENTION_CHECK, 'correct')

        assignment2 = MockAssignment(assignment_id = 2)
        assignment2.add_answer(URL_FOUND, 'yes')
        assignment2.add_answer(URL, 'http://www.libertylounge.com/')
        assignment2.add_answer(ATTENTION_CHECK, 'correct')

        assignment3 = MockAssignment(assignment_id = 3)
        assignment3.add_answer(URL_FOUND, 'yes')
        assignment3.add_answer(URL, 'http://libertylounge.com')
        assignment3.add_answer(ATTENTION_CHECK, 'incorrect')

        assignments = [ assignment1, assignment2, assignment3 ]

        result = mturk_utilities.process_find_website_hit_assignments(
            mock_connection, mturk_location, assignments)

        self.assertEqual(result, None)
        mock_connection.reject_assignment.assert_called_with(3, 'Failed attention check question.')
        mock_connection.extend_hit.assert_called_with("HIT_Id", assignments_increment = 1)

