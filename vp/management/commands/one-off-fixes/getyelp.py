from django.core.management.base import BaseCommand
from vp.models import Location
from viceprice import settings
import json
import urllib
import urllib2
import oauth2
import unicodecsv as csv

API_HOST = 'api.yelp.com'
DEFAULT_LOCATION = 'Washington, DC'
SEARCH_LIMIT = 10
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = settings.YELP_CONSUMER_KEY
CONSUMER_SECRET = settings.YELP_CONSUMER_SECRET
TOKEN = settings.YELP_TOKEN
TOKEN_SECRET = settings.YELP_TOKEN_SECRET

class Command(BaseCommand):

    def request(self, host, path, url_params=None):
        """Prepares OAuth authentication and sends the request to the API.
        Args:
            host (str): The domain host of the API.
            path (str): The path of the API after the domain.
            url_params (dict): An optional set of query parameters in the request.
        Returns:
            dict: The JSON response from the request.
        Raises:
            urllib2.HTTPError: An error occurs from the HTTP request.
        """
        url_params = url_params or {}
        url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        oauth_request = oauth2.Request(
            method="GET", url=url, parameters=url_params)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': TOKEN,
                'oauth_consumer_key': CONSUMER_KEY
            }
        )
        token = oauth2.Token(TOKEN, TOKEN_SECRET)
        oauth_request.sign_request(
            oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()

        print u'Querying {0} ...'.format(url)

        conn = urllib2.urlopen(signed_url, None)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()

        return response


    def search(self, term, location = DEFAULT_LOCATION):
        """Query the Search API by a search term and location.
        Args:
            term (str): The search term passed to the API.
            location (str): The search location passed to the API.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': term.replace(' ', '+'),
            'location': location.replace(' ', '+'),
            'limit': SEARCH_LIMIT
        }
        return self.request(API_HOST, SEARCH_PATH, url_params=url_params)

    def find_match(self, location, responses):
        for response in responses:

            # Try match name
            if location.name != None and response.get('name') != None and location.name.lower() == response.get('name').lower():
                return response

            # Try match phone number
            if (location.formattedPhoneNumber != None and response.get('display_phone') != None and
                location.formattedPhoneNumber.replace('(', '').replace(')', '').replace('-', '')
                == response.get('display_phone').replace("+1", '').replace('(', '').replace(')', '').replace('-', '')):
                return response

            # Try match lat/long
            if (response.get('location') != None and response['location'].get('coordinate') != None):
                if (abs(location.latitude - response['location']['coordinate']['latitude']) < 0.001 and
                    abs(location.longitude - response['location']['coordinate']['longitude']) < 0.001):
                    return response

    def get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = BUSINESS_PATH + business_id

        return self.request(API_HOST, business_path)


    # Update all location data that needs to be updated
    def update_locations(self):

        locations = Location.objects.all()

        for location in locations:
            responses = self.search(location.name)

            if (responses != None and responses.get('businesses') != None and len(responses.get('businesses')) > 0):
                result = self.find_match(location, responses['businesses'])
                if (result != None and result.get('id') != None):
                    location.yelpId = result['id']
                    print(location.name)
                    print(location.yelpId)
                    location.save()


    def write_attributes_to_csv(self):

        with open('yelp_data.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Name', 'Categories', '', '', '', '', '', 'Neighborhoods'])

            locations = Location.objects.all()

            for location in locations:
                if location.yelpId != None:
                    data = self.get_business(location.yelpId)
                    row = [location.id, location.name]

                    categories = data.get('categories')
                    if categories != None and len(categories) > 0:
                        for category in categories:
                            print(category[0])
                            row.append(category[0])
                        for i in range(6 - len(categories)):
                            row.append('')
                    else:
                        for i in range(6):
                            row.append('')

                    neighborhoods = data['location'].get('neighborhoods')
                    if neighborhoods != None and len(neighborhoods) > 0:
                        for neighborhood in neighborhoods:
                            print(neighborhood)
                            row.append(neighborhood)

                    writer.writerow(row)

            csvfile.close()


    def handle(self, *args, **options):
        #self.update_locations()
        self.write_attributes_to_csv()