from django.core.management.base import BaseCommand
from vp.models import Location, LocationCategory
from viceprice import settings
import facebook
import urllib
import urlparse
import subprocess
import warnings
import time


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

        access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
        graph = facebook.GraphAPI(access_token)
        inaccessible_locations = []

        for location in Location.objects.order_by('id').all():
            if location.facebookId != None and location.facebookId != "":
                try:
                    args = {'fields': 'category, category_list' }

                    try:
                        page = graph.get_object(location.facebookId, **args)
                    except:
                        inaccessible_locations.append(location.name)
                        continue

                    base_category, created = LocationCategory.objects.get_or_create(
                        name = page['category'],
                        isBaseCategory = True
                    )
                    if created:
                        base_category.save()

                    location.locationCategories.clear()
                    location.locationCategories.add(base_category)

                    for category in page['category_list']:
                        sub_category, created = LocationCategory.objects.get_or_create(
                            name = category['name'],
                            facebookCategoryId = category['id'],
                            isBaseCategory = False,
                            parentCategory = base_category
                        )
                        if created:
                            sub_category.save()

                        location.locationCategories.add(sub_category)

                    location.save()

                except KeyError:
                    print('Unable to access Facebook data')
                    continue

                # Pause so Facebook doesn't kick us off
                time.sleep(1)


    def handle(self, *args, **options):
        self.get_facebook_categories()