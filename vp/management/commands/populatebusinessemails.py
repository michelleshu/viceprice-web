from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from vp.models import Location
from viceprice import settings
import unicodecsv as csv

class Command(BaseCommand):

    # Write business email data from file
    def update_businessemails(self):
        with open('vp/management/commands/BizEmailsOct10.csv', 'rb') as datafile:
            reader = csv.reader(datafile)
            for row in reader:
                location_id = row[0]
                location = Location.objects.get(id = location_id)
                
                if (location != None):
                    location.businessEmail = row[1]
                    location.save()
                    print('Saved Business Email for ' + location.name)

    def handle(self, *args, **options):
        self.update_businessemails()