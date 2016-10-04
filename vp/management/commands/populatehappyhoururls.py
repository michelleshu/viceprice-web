from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from vp.models import Location
from viceprice import settings
import unicodecsv as csv

class Command(BaseCommand):

    # Write happy hour URL data from file
    def update_happyhoursurls(self):
        with open('vp/management/commands/UpdateHHURLSJIRA.csv', 'rb') as datafile:
            reader = csv.reader(datafile)
            for row in reader:
                location_id = row[0]
                location = Location.objects.get(id = location_id)
                if (location != None):
                    location.happyHourWebsite = row[4]
                    location.save()
                    print('Saved Happy Hour URL for ' + location.name)


    def handle(self, *args, **options):
        self.update_happyhoursurls()