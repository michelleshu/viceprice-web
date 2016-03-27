from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from models import Location, BusinessHour, LocationCategory, TimeFrame, DayOfWeek, Deal, DealDetail
import json
import pprint
import pdb
@login_required(login_url='/login/')
def index(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return enter_happy_hour_view(request)

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
                .filter(latitude__range=[min_lat, max_lat], longitude__range=[min_lng, max_lng])
                .order_by('pk')[:50]
            )

        locations = [ location_info_to_dict(l) for l in locations ]

        return HttpResponse(json.dumps(locations), content_type="application/json")

def get_all_locations():
    return Location.objects.all()

# Custom mapping from Location and Address objects to JSON-serializable view info
def location_info_to_dict(location):
    return {
        'name': location.name,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'address': model_to_dict(location.address),
        'phone_number': location.phone_number,
        'website': location.website,
        'business_hours': [ model_to_dict(bh) for bh in list(location.business_hours.all()) ],
        'approved': location.approved
    }

# Utility to add foursquare ids to our database and pull initial data
def upload_data_view(request):
    location_categories = LocationCategory.objects.all()
    context = { 'location_categories': list(location_categories) }
    context.update(csrf(request))

    return render_to_response('upload_data.html', context)

def fetch_locations(request):
    locations = Location.objects.all()
    jsons = []
    for location in locations:
        json = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [location.longitude, location.latitude]}, "properties": {"name": location.name, "website":location.website, "phone": location.formattedPhoneNumber, "neighborhood":location.neighborhood, "icon": {"className": "pin", "iconSize": ""}}}
        jsons.append(json)
    return JsonResponse({'json':jsons})

def sandbox(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('sandbox.html', context)

def home(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('home.html', context)


# Manual Happy Hour Entry

@login_required(login_url='/login/')
def enter_happy_hour_view(request):
    context = {}
    context.update(csrf(request))

    return render_to_response('enter_happy_hour.html', context)


def get_location_that_needs_happy_hour(request):
    locations = Location.objects.filter(dealDataManuallyReviewed=None).order_by('?')
    selected = locations.first()

    response = {
        'remaining_count': locations.count(),
        'location_id': selected.id,
        'location_name': selected.name,
        'location_website': selected.website,
        'location_phone_number': selected.formattedPhoneNumber
    }
    return JsonResponse(response)

@csrf_exempt
def submit_happy_hour_data(request):
    data = json.loads(request.body)

    DRINK_CATEGORIES = {
        "beer": 1,
        "wine": 2,
        "liquor": 3
    }

    DEAL_TYPES = {
        "price": 1,
        "percent-off": 2,
        "price-off": 3
    }

    location_id = data.get('location_id')
    location = Location.objects.get(id = location_id)

    deals = data.get('deals')
    # loop over all the deals posted to the server
    for deal in deals:
        time_period_data = deal.get('timePeriods')
        time_periods = []
        #loop over all the time periods for a deal
        for tp_data in time_period_data:
            #push the time periods to the time_periods array
            time_periods.append({
                    'start': tp_data.get("startTime"),
                 'end': tp_data.get("endTime"),
                 'until_close': tp_data.get("untilClose")
             })
        #pass the time_periods array and the 'daysOfWeek' array from the request body to a BusinessHour object
        deal_hour = BusinessHour.objects.create(time_periods, deal.get('daysOfWeek'))
        #save the deal_hour
        deal_hour.save()

        #instantiate a new deal object and fill in as needed
        newdeal = Deal()
        #set the Deal's deal_hour to the BuinessHour object from before (deal_hour)
        newdeal.dealHour = deal_hour
        #dummy for description
        newdeal.description = ""
        #try to save the deal
        newdeal.save()
        deal_detail_data = deal.get('dealDetails')

        for detail in deal_detail_data:
            drink_names = detail.get("names")
            category = DRINK_CATEGORIES[detail.get("category")]
            type = DEAL_TYPES[detail.get("dealType")]

            dealDetail = DealDetail(deal=newdeal, drinkName=drink_names, drinkCategory=category, type=type, value=detail.get("dealValue"))
            dealDetail.save()

        location.deals.add(newdeal)

    location.dealDataManuallyReviewed = timezone.now()
    location.save()

    return HttpResponse("success")

@csrf_exempt
def submit_locations_to_upload(request):
    data = request.POST

    # For every Foursquare ID entered in the form, insert into database if it doesn't already exist
    location_foursquare_ids = data.get('location-foursquare-ids').splitlines()
    location_category_id = int(data.get('location-category'))

    for foursquare_id in location_foursquare_ids:
        location, created = Location.objects.get_or_create(foursquareId=foursquare_id.strip())
        location_category = LocationCategory.objects.get(id=location_category_id)
        location.locationCategories.add(location_category)
        location.save()

    return HttpResponse("Success")
