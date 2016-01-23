from django.core.management.base import BaseCommand
from django.utils import timezone
from vp.models import Location, BusinessHour
from viceprice import settings
import requests
import time

class Command(BaseCommand):

    # Update all location data that needs to be updated
    def update_locations(self):

        # Get all locations that have no Foursquare data
        foursquare_locations = Location.objects.all()

        for location in foursquare_locations:
            print('Retrieving data for "%s"' % location.foursquareId)
            response = (requests.get("https://api.foursquare.com/v2/venues/" + location.foursquareId,
                params = {
                    'client_id': settings.FOURSQUARE_CLIENT_ID,
                    'client_secret': settings.FOURSQUARE_CLIENT_SECRET,
                    'v': '20151003',
                    'm': 'foursquare'
                })
                .json())['response']

            data = response.get('venue')
            if data != None:
                location.formattedPhoneNumber = data['contact'].get('formattedPhone')
                location.save()

                print('Updated "%s"' % location.name)
                time.sleep(0.5)

    def handle(self, *args, **options):
        self.update_locations()