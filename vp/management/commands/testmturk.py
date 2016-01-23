from django.core.management.base import BaseCommand
from optparse import make_option
from vp.models import MTurkLocationInfo
from random import randint

NAME = 'VicePrice Test HIT'
ADDRESS = '1234 1st St\nWashington, D.C. 20003'
DEFAULT_URL = 'http://www.website.com'
DEFAULT_PHONE_NUMBER = '(111)222-3333'
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
        mturk_location = self.add_mturk_location(options)


    def add_mturk_location(self, options):
        mturk_location = MTurkLocationInfo(
            foursquare_id = 'RANDID' + str(randint(100, 999)),
            name = NAME,
            address = ADDRESS,
            url = DEFAULT_URL,
            url_provided = True,
            phone_number = DEFAULT_PHONE_NUMBER,
            stage = DEFAULT_STAGE,
            get_hh_attempts = 0,
            deals_confirmations = 0
        )

        if (hasattr(options, 'no-url') and options['no-url']):
            mturk_location.url = None
            mturk_location.url_provided = False

        if (hasattr(options, 'no-phone-number') and options['no-phone-number']):
            mturk_location.phone_number = None

        if (hasattr(options, 'stage')):
            mturk_location.stage = options['stage']

        if (hasattr(options, 'attempts')):
            mturk_location.get_hh_attempts = options['attempts']

        if (hasattr(options, 'confirmations')):
            mturk_location.deals_confirmations = options['confirmations']

        return mturk_location
