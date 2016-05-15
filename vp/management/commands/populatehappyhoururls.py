from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from vp.models import Location
from viceprice import settings
import unicodecsv as csv

class Command(BaseCommand):

    # Write Facebook data from file
    def update_happyhoursurls(self):
        with open('HappyHourURLS.csv', 'rb') as datafile:
            reader = csv.reader(datafile)
            for row in reader:
                location_name = row[0]
                locations = Location.objects.filter(name = location_name).all()

                if len(locations) != 1:
                    print('Zero or multiple locations returned: ' + str(location_name))
                    continue

                location = locations.first()
                location.happyHourWebsite = row[1]
                location.save()


    def handle(self, *args, **options):
        self.update_happyhoursurls()