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
from django.db.models import Q, F
from models import Location, BusinessHour, LocationCategory, TimeFrame, DayOfWeek, Deal, DealDetail, ActiveHour
import json
import pprint

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
    time = request.GET.get('time')
    day = request.GET.get('day')
    locations = Location.objects.filter(Q(deals__activeHours__dayofweek=day), Q(deals__activeHours__start__lte=time), Q(deals__activeHours__end__gte=time) | Q(deals__activeHours__end__lte=F('deals__activeHours__start'))).distinct().prefetch_related('deals__dealDetails')
    container = []
    barLocations = []
    dealInfo = []
    for location in locations:
        dealList = []
        dealSet = location.deals.all()
        for d in dealSet:
            dealDetails = d.dealDetails.all()
            details = []
            for d in dealDetails:
                detail = {"detail_id":d.id,
                          "drinkName": d.drinkName,
                          "drinkCategory":d.drinkCategory,
                          "detaiType":d.detailType,
                          "value":d.value}
                details.append(detail)
            deals = {"deal_id" : d.id,
                    "details": details }
            dealList.append(deals)
        dealData = {
        "locationid": location.id,
        "deals": dealList}
        dealInfo.append(dealData)
        addressCityIndex = location.formattedAddress.find("Washington,")
        abbreviatedAddress = location.formattedAddress[:addressCityIndex]
    
        locationData = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [location.longitude, location.latitude]
            },
            "properties": {
                "name": location.name,
                "website":location.website,
                "phone": location.formattedPhoneNumber,
                "fullAddress": location.formattedAddress,
                "abbreviatedAddress": abbreviatedAddress,
                "neighborhood":location.neighborhood,
                "icon": {"className": "pin", "iconSize": ""}
            }
        }
        barLocations.append(locationData)
    container.append(barLocations)
    container.append(dealInfo)
    return JsonResponse({'json':barLocations, 'deals':dealInfo})

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

def flag_location_as_skipped(request):
    data = json.loads(request.body)
    location_id = data.get('location_id')
    location = Location.objects.get(id=location_id)
    location.data_entry_skipped = True
    location.save()
    return HttpResponse("success")  
 
def get_location_that_needs_happy_hour(request):
    locations = Location.objects.filter(data_entry_skipped=False, dealDataManuallyReviewed=None).order_by('?')
    selected = locations.first()

    response = {
        'remaining_count': locations.count(),
        'location_id': selected.id,
        'location_name': selected.name,
        'location_website': selected.website,
        'location_phone_number': selected.formattedPhoneNumber,
        'location_address': selected.formattedAddress
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
    location = Location.objects.get(id=location_id)
    deals = data.get('deals')
    # loop over all the deals posted to the server
    for deal in deals:
        # loop over all the time periods for a deal
        newdeal = Deal()
        newdeal.save()
        for day in deal.get('daysOfWeek'):
            for tp_data in deal.get('timePeriods'):
                # push the time periods to the time_periods array
                activeHour = ActiveHour()
                activeHour.dayofweek = day
                activeHour.start = tp_data.get("startTime")
                activeHour.end = tp_data.get("endTime")
              
                if activeHour.end == "":
                    activeHour.end = None
                activeHour.save()
                newdeal.activeHours.add(activeHour)
        newdeal.description = ""
        deal_detail_data = deal.get('dealDetails')
        for detail in deal_detail_data:
            drink_names = detail.get("names")
            category = DRINK_CATEGORIES[detail.get("category")]
            type = DEAL_TYPES[detail.get("dealType")]
            dealDetail = DealDetail(drinkName=drink_names, drinkCategory=category, detailType=type, value=detail.get("dealValue"))
            dealDetail.save()
            newdeal.dealDetails.add(dealDetail)
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
