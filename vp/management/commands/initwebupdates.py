from django.core.management.base import BaseCommand
from django.db.models import Q
from vp.models import *
from datetime import timedelta

EXPIRATION_PERIOD = 30 # Days it takes for data to expire

class Command(BaseCommand):
    help = 'Kicks off Foursquare and Mechanical Turk website tasks for all locations that require updates'
    args = '<site>'

    # Get locations that require updates
    def get_mturk_locations_to_update(self):
        earliest_unexpired_date = timezone.now() - timedelta(days=EXPIRATION_PERIOD)

        # Get all locations that have either just been added or expired
        foursquare_locations = Location.objects.filter(Q(name__isnull=True) | Q(dateLastUpdated__lt=earliest_unexpired_date))

        # Convert these locations to MTurk location



    def handle(self, *args, **options):
        pass
        # Fill in