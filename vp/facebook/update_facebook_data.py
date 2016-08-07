from vp.models import Location, ActiveHour
from viceprice import settings
import facebook
import urllib
import urlparse
import subprocess
import warnings
import time
import django

def update():

    django.setup()

    warnings.filterwarnings('ignore', category=DeprecationWarning)

    # Trying to get an access token. Very awkward.
    oauth_args = dict(client_id     = settings.FACEBOOK_APP_ID,
                      client_secret = settings.FACEBOOK_APP_SECRET,
                      grant_type    = 'client_credentials')
    oauth_curl_cmd = ['curl',
                      'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
    oauth_response = subprocess.Popen(oauth_curl_cmd,
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE).communicate()[0]

    access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
    graph = facebook.GraphAPI(access_token)
    inaccessible_locations = []

    for location in Location.objects.all():
        if location.facebookId != None and location.facebookId != "":
            try:
                args = {'fields': 'hours, cover, location, emails' }

                try:
                    page = graph.get_object(location.facebookId, **args)
                except:
                    inaccessible_locations.append(location.name)
                    continue

                if page.get("hours") != None:
                    save_active_hours(location, page["hours"])
                if page.get("location") != None:
                    save_address_data(location, page["location"])
                if page.get("cover") != None:
                    save_cover_photo(location, page["cover"])
                if page.get("emails") != None:                
                    if (len(page["emails"]) > 0):
                        location.business_email = page["emails"][0]

                location.save()

            except KeyError:
                print('Unable to access Facebook data')
                continue

            # Pause so Facebook doesn't kick us off
            time.sleep(1)

def save_active_hours(location, active_hours):
    location.activeHours.clear()
    if (active_hours.get("mon_1_open") != None and active_hours.get("mon_1_close") != None):
        activeHour = ActiveHour(dayofweek=1, start=active_hours["mon_1_open"], end=active_hours["mon_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("mon_2_open") != None and active_hours.get("mon_2_close") != None):
        activeHour = ActiveHour(dayofweek=1, start=active_hours["mon_2_open"], end=active_hours["mon_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("tue_1_open") != None and active_hours.get("tue_1_close") != None):
        activeHour = ActiveHour(dayofweek=2, start=active_hours["tue_1_open"], end=active_hours["tue_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("tue_2_open") != None and active_hours.get("tue_2_close") != None):
        activeHour = ActiveHour(dayofweek=2, start=active_hours["tue_2_open"], end=active_hours["tue_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("wed_1_open") != None and active_hours.get("wed_1_close") != None):
        activeHour = ActiveHour(dayofweek=3, start=active_hours["wed_1_open"], end=active_hours["wed_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("wed_2_open") != None and active_hours.get("wed_2_close") != None):
        activeHour = ActiveHour(dayofweek=3, start=active_hours["wed_2_open"], end=active_hours["wed_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("thu_1_open") != None and active_hours.get("thu_1_close") != None):
        activeHour = ActiveHour(dayofweek=4, start=active_hours["thu_1_open"], end=active_hours["thu_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("thu_2_open") != None and active_hours.get("thu_2_close") != None):
        activeHour = ActiveHour(dayofweek=4, start=active_hours["thu_2_open"], end=active_hours["thu_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("fri_1_open") != None and active_hours.get("fri_1_close") != None):
        activeHour = ActiveHour(dayofweek=5, start=active_hours["fri_1_open"], end=active_hours["fri_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("fri_2_open") != None and active_hours.get("fri_2_close") != None):
        activeHour = ActiveHour(dayofweek=5, start=active_hours["fri_2_open"], end=active_hours["fri_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("sat_1_open") != None and active_hours.get("sat_1_close") != None):
        activeHour = ActiveHour(dayofweek=6, start=active_hours["sat_1_open"], end=active_hours["sat_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("sat_2_open") != None and active_hours.get("sat_2_close") != None):
        activeHour = ActiveHour(dayofweek=6, start=active_hours["sat_2_open"], end=active_hours["sat_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    if (active_hours.get("sun_1_open") != None and active_hours.get("sun_1_close") != None):
        activeHour = ActiveHour(dayofweek=7, start=active_hours["sun_1_open"], end=active_hours["sun_1_close"])
        activeHour.save()
        location.activeHours.add(activeHour)
    if (active_hours.get("sun_2_open") != None and active_hours.get("sun_2_close") != None):
        activeHour = ActiveHour(dayofweek=7, start=active_hours["sun_2_open"], end=active_hours["sun_2_close"])
        activeHour.save()
        location.activeHours.add(activeHour)

    location.save()

def save_address_data(location, address):
    if (address.get("city") != None):
        location.city = address["city"]
    if (address.get("state") != None):
        location.state = address["state"]
    if (address.get("street") != None):
        location.street = address["street"]
    if (address.get("zip") != None):
        location.zip = address["zip"]
    if (address.get("latitude") != None):
        location.latitude = address["latitude"]
    if (address.get("longitude") != None):
        location.longitude = address["longitude"]

    location.save()

def save_cover_photo(location, cover):
    if (cover.get("source") != None):
        location.coverPhotoSource = cover["source"]
    if (cover.get("offset_x") != None):
        location.coverXOffset = int(cover["offset_x"])
    if (cover.get("offset_y") != None):
        location.coverYOffset = int(cover["offset_y"])

    location.save()
