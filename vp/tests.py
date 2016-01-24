import datetime
from django.conf import settings
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone
from models import Location, MTurkLocationInfo
from mturk import mturk_utilities
from boto.mturk import connection
from viceprice.constants import *

# TO RUN A SPECIFIC TEST:
# ./manage.py test vp.tests.Test.test_function

# MTurk Tests

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
        location = MTurkLocationInfo.objects.get(name = "Liberty Lounge")
        mturk_utilities.create_hit(self.conn, location, settings.MTURK_HIT_TYPES[FIND_WEBSITE])




# Test Stage 0: Find URL of MTurk
class MTurkFindURLTest(TestCase):
    def setUp(self):
        # Location that we find URL for
        found_location = Location.objects.create(name = "FindURLFound")
        # Location that we do not find URL for
        not_found_location = Location.objects.create(name = "FindURLNotFound")

        MTurkLocationInfo.objects.create(location = found_location, name = "FindURLFound", stage = 0)
        MTurkLocationInfo.objects.create(location = not_found_location, name = "FindURLNotFound", stage = 0)