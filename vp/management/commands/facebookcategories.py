from django.core.management.base import BaseCommand
from vp.models import Location, LocationCategory
from viceprice import settings
import facebook
import urllib
import urlparse
import subprocess
import warnings


class Command(BaseCommand):
    args = '<site>'
    app_id = settings.FACEBOOK_APP_ID
    app_secret = settings.FACEBOOK_APP_SECRET

    def get_facebook_categories(self):
        warnings.filterwarnings('ignore', category=DeprecationWarning)

        # Trying to get an access token. Very awkward.
        oauth_args = dict(client_id     = self.app_id,
                          client_secret = self.app_secret,
                          grant_type    = 'client_credentials')
        oauth_curl_cmd = ['curl',
                          'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
        oauth_response = subprocess.Popen(oauth_curl_cmd,
                                          stdout = subprocess.PIPE,
                                          stderr = subprocess.PIPE).communicate()[0]

        try:
            access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
            graph = facebook.GraphAPI(access_token)
            args = {'fields': 'category, category_list' }
            page = graph.get_object('creme14th', **args)
            print(page['category'])

            #base_category = LocationCategory.objects.get_or_create(name=)

            for subcategory in page['category_list']:
                print subcategory['id']
                print subcategory['name']

        except KeyError:
            print('Unable to grab an access token')
            exit()


    def handle(self, *args, **options):
        self.get_facebook_categories()