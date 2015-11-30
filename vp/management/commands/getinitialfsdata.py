from django.core.management.base import BaseCommand
from django.utils import timezone
from models import Location, BusinessHour
from viceprice import settings
import requests

class Command(BaseCommand):
    help = 'Kicks off Foursquare and Mechanical Turk website tasks for all locations that require updates'

    def update_business_hours(self, location):
        business_hours = location.businessHours.all()

        # Delete all old business hours info
        for h in business_hours:
            h.time_frames.all().delete()
            h.days_of_week.all().delete()

        business_hours.delete()

        # Get new business hours info
        data = (requests.get("https://api.foursquare.com/v2/venues/" + location.foursquareId + "/hours",
            params = {
                'client_id': settings.FOURSQUARE_CLIENT_ID,
                'client_secret': settings.FOURSQUARE_CLIENT_SECRET,
                'v': '20151003',
                'm': 'foursquare'
            })
            .json())

        if data['response']['hours'].get('timeframes') != None:
            for d in data['response']['hours']['timeframes']:
                location.businessHours.add(BusinessHour.objects.create(d['open'], d['days']))

    # Update all location data that needs to be updated
    def update_locations(self):

        # Get all locations that have no Foursquare data
        foursquare_locations = Location.objects.filter(name__isnull=True)

        for location in foursquare_locations:
            data = (requests.get("https://api.foursquare.com/v2/venues/" + location.foursquareId,
                params = {
                    'client_id': settings.FOURSQUARE_CLIENT_ID,
                    'client_secret': settings.FOURSQUARE_CLIENT_SECRET,
                    'v': '20151003',
                    'm': 'foursquare'
                })
                .json())['response']['venue']

            location.name = data.get('name')
            location.latitude = data['location'].get('lat')
            location.longitude = data['location'].get('lng')

            if (data['location'].get('formattedAddress') != None):
                location.formattedAddress = "\n".join(data['location']['formattedAddress'])

            location.formattedPhoneNumber = data['contact'].get('formattedPhone')
            location.website = data.get('url')
            location.rating = data.get('rating')
            location.foursquareDateLastUpdated = timezone.now()

            location.save()

            self.update_business_hours(location)

    def handle(self, *args, **options):
        self.update_locations()