from django.core.management.base import BaseCommand
from optparse import make_option
from vp.models import MTurkLocationInfo
from random import randint

TEST_LOCATION_ID =
NAME = 'Liberty Lounge'
ADDRESS = '3257 Stanton Rd SE,\nWashington, D.C. 20020'
DEFAULT_URL = 'http://www.justinhinh.com'
DEFAULT_PHONE_NUMBER = '(202)790-4414'
DEFAULT_STAGE = 1

class Command(BaseCommand):
    help = 'Tests'
    args = '<site>'
    option_list = BaseCommand.option_list + \
        (
            make_option('--no-url', action="store_true", dest="no_url", default=False),
        ) + \
        (
            make_option('--no-phone', action="store_true", dest="no_phone", default=False),
        ) + \
        (
            make_option('--stage', action="store", type="int", dest="stage"),
        ) + \
        (
            make_option('--attempts', action="store", type="int", dest="attempts"),
        ) + \
        (
            make_option('--confirmations', action="store", type="int", dest="confirmations"),
        )

    def handle(self, *args, **options):
        mturk_location = self.create_mturk_location(options)


    def create_mturk_location(self, options):
        mturk_location = MTurkLocationInfo(
            foursquare_id = 'RANDID' + str(randint(100, 999)),
            name = NAME,
            address = ADDRESS,
            url = DEFAULT_URL,
            phone_number = DEFAULT_PHONE_NUMBER,
            stage = DEFAULT_STAGE,
            confirmations = 0
        )

        if (hasattr(options, 'no-url') and options['no-url']):
            mturk_location.url = None

        if (hasattr(options, 'no-phone-number') and options['no-phone-number']):
            mturk_location.phone_number = None

        if (hasattr(options, 'stage')):
            mturk_location.stage = options['stage']

        if (hasattr(options, 'confirmations')):
            mturk_location.confirmations = options['confirmations']

        return mturk_location
