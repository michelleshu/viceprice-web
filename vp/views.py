from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from models import Location, LocationCategory, BusinessHour
import json
import requests

@login_required(login_url='/login/')
def index(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return upload_data_view(request)

# Authentication
def login_view(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('login.html', context)

def register_view(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('register.html', context)

def authenticate_user(request, onsuccess='/', onfail='/login/'):
    post = request.POST
    user = authenticate(username=post['username'], password=post['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)

def register_user(request):
    post = request.POST
    if not user_exists(post['username']):
        create_user(username=post['username'], email=post['email'], password=post['password'])
        return authenticate_user(request)
    else:
        return redirect("/login/")

def logout_user(request, redirect_url='/login'):
    logout(request)
    return redirect(redirect_url)

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

def user_exists(username):
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True

# Update all location data that needs to be updated
def update_locations(request):
    earliest_unexpired_date = timezone.now() - timedelta(days=30)

    # Get all locations that have either just been added or expired
    foursquare_locations = Location.objects.filter(Q(name__isnull=True) | Q(dateLastUpdated__lt=earliest_unexpired_date))

    response = HttpResponse()
    response.write("<h3>Updated locations:</h3>")

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
        location.dateLastUpdated = timezone.now()

        location.save()

        update_business_hours(location)

        response.write("<p>" + location.name + " updated</p>")

    return response

def update_business_hours(location):
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

    return HttpResponse('')

# Request locations within map viewport
def get_locations_within_bounds(request):
    if request.is_ajax():
        min_lat = request.POST['min_lat']
        max_lat = request.POST['max_lat']
        min_lng = request.POST['min_lng']
        max_lng = request.POST['max_lng']

        locations = list(
            Location.objects
                .select_related('address')
                .filter(latitude__range = [min_lat, max_lat], longitude__range = [min_lng, max_lng])
                .order_by('pk')[:50]
            )

        locations = [ location_info_to_dict(l) for l in locations ]

        return HttpResponse(json.dumps(locations), content_type="application/json")

# Custom mapping from Location and Address objects to JSON-serializable view info
def location_info_to_dict(location):
    return {
        'name': location.name,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'address': model_to_dict(location.address),
        'phone_number': location.phone_number,
        'website': location.website,
        'business_hours': [ model_to_dict(bh) for bh in list(location.product_categories.all()) ],
        'approved': location.approved
    }

# Utility to add foursquare ids to our database and pull initial data
def upload_data_view(request):
    location_categories = LocationCategory.objects.all()
    context = { 'location_categories': list(location_categories) }
    context.update(csrf(request))

    return render_to_response('upload_data.html', context)

def submit_locations_to_upload(request):
    data = request.POST

    # For every Foursquare ID entered in the form, insert into database if it doesn't already exist
    location_foursquare_ids = data.get('location-foursquare-ids').splitlines()
    location_category = int(data.get('location-category'))

    for foursquare_id in location_foursquare_ids:
        location, created = Location.objects.get_or_create(foursquareId = foursquare_id.strip())
        location.category_id = location_category
        location.save()

    return update_locations(request)

