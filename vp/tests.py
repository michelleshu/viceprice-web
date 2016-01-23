from django.conf import settings
from django.test import TestCase
from models import Location, MTurkLocationInfo
from mturk import mturk_utilities
from boto.mturk import connection
from viceprice.constants import *

# TO RUN A SPECIFIC TEST:
# ./manage.py test vp.tests.TestCase.test_function

# MTurk Tests



# Test creation of HIT layouts
# Manually check the layout appearance on development sandbox
# Then the HITs on Amazon can be deleted using the management command disablehits
class HITCreationTestCase(TestCase):
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
class MTurkFindURLTestCase(TestCase):
    def setUp(self):
        # Location that we find URL for
        found_location = Location.objects.create(name = "FindURLFound")
        # Location that we do not find URL for
        not_found_location = Location.objects.create(name = "FindURLNotFound")

        MTurkLocationInfo.objects.create(location = found_location, name = "FindURLFound", stage = 0)
        MTurkLocationInfo.objects.create(location = not_found_location, name = "FindURLNotFound", stage = 0)

    def tearDown(self):
        MTurkLocationInfo.objects.get(name = "FindURLFound").delete()
        MTurkLocationInfo.objects.get(name = "FindURLNotFound").delete()
        Location.objects.get(name = "FindURLFound").delete()
        Location.objects.get(name = "FindURLNotFound").delete()