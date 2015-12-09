from django.core.management.base import BaseCommand
from django.db.models import Q
from vp.models import *
from vp.mturk.mturk_update_website_tasks import *
from datetime import timedelta
from django.utils import timezone
import updatedb

EXPIRATION_PERIOD = 30 # Days it takes for data to expire

# Get locations that require updates
def get_mturk_locations_to_update():
    earliest_unexpired_date = timezone.now() - timedelta(days=EXPIRATION_PERIOD)

    # Get all locations that have either just been added or expired
    foursquare_locations = Location.objects.filter(Q(mturkLastUpdateCompleted__isnull=True) | Q(mturkLastUpdateCompleted__lt=earliest_unexpired_date))

    # DEBUG
    foursquare_locations = foursquare_locations[0:10]

    # Convert these locations to MTurk location
    mturk_locations = [];
    for location in foursquare_locations:
        mturk_locations.append(MTurkLocation(
            foursquare_id = location.foursquareId,
            name = location.name,
            address = location.formattedAddress,
            phone_number = location.formattedPhoneNumber,
            check_ins = location.checkIns,
            rating = location.rating
        ))

        # Update mturk date updated to current date to indicate that it is being updated and avoid picking it up again
        location.mturkLastUpdateCompleted = timezone.now()
        location.save()

    return mturk_locations


def run_website_update():
    locations_to_update = get_mturk_locations_to_update()
    write_location_objects_to_csv(locations_to_update, UPDATED_WEBSITE_DATA_FILE, append=True)
    update_website_tasks(locations_to_update)
    updatedb.write_mturk_deals_to_db()


class Command(BaseCommand):
    help = 'Runs Mechanical Turk tasks for all website locations that require updates and writes completed info to db'
    args = '<site>'

    def handle(self, *args, **options):
        run_website_update()

run_website_update();

