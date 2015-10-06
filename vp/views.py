from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from models import Location, BusinessHour, TimeFrame, DayOfWeek
import json
import requests

@login_required(login_url='/login/')
def index(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return render_to_response('map.html', context)

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
    foursquare_locations = Location.objects.all()

    for location in foursquare_locations:
        data = (requests.get("https://api.foursquare.com/v2/venues/" + location.foursquareId,
            params = {
                'client_id': settings.FOURSQUARE_CLIENT_ID,
                'client_secret': settings.FOURSQUARE_CLIENT_SECRET,
                'v': '20151003',
                'm': 'foursquare'
            })
            .json())['response']['venue'];

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

    return HttpResponse('')

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