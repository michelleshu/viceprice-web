from django.core.context_processors import csrf
from django.db import connection
from django.db.models import Count
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F, Count
from models import Location, LocationCategory, Deal, DealDetail, ActiveHour
from revproxy.views import ProxyView
import json
import logging
import collections
from yelpapi import YelpAPI 

logger = logging.getLogger(__name__)

def about(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('about.html', context)

# Authentication
def login_view(request):
    context = {}
    context.update(csrf(request))
    request.session['next'] = request.GET['next']
    logger.error(request.session)
    return render_to_response('login.html', context)

def register_view(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('register.html', context)

def authenticate_user(request, onsuccess='/data_entry/', onfail='/login/'):
    post = request.POST
    user = authenticate(username=post['username'], password=post['password'])
    if user is not None:
        login(request, user)
        onsuccess = request.session.get('next', onsuccess)
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


def fetch_filtered_deals(request):
    neighborhood = request.GET.get('neighborhood')
    time = request.GET.get('time')
    day = request.GET.get('day')

    query = "SELECT l.\"id\", l.\"name\", l.\"latitude\", l.\"longitude\", l.\"website\", \
        l.\"happyHourWebsite\", l.\"street\", l.\"coverPhotoSource\", l.\"coverXOffset\", l.\"coverYOffset\", \
        d.\"id\", ah.\"start\", ah.\"end\", dd.\"drinkName\", dd.\"drinkCategory\", dd.\"detailType\", dd.\"value\" \
        FROM \"vp_location\" l \
        JOIN \"vp_location_deals\" ld \
        ON l.\"id\" = ld.\"location_id\" \
        JOIN \"vp_deal\" d \
        ON d.\"id\" = ld.\"deal_id\" \
        JOIN \"vp_deal_activeHours\" dah \
        ON d.\"id\" = dah.\"deal_id\" \
        JOIN \"vp_activehour\" ah \
        ON ah.\"id\" = dah.\"activehour_id\" \
        JOIN \"vp_deal_dealDetails\" ddd \
        ON d.\"id\" = ddd.\"deal_id\" \
        JOIN \"vp_dealdetail\" dd \
        ON dd.\"id\" = ddd.\"dealdetail_id\" \
        WHERE d.\"dealSource\" = 1 AND l.\"neighborhood\" = \'" + str(neighborhood) + "\'"

    if (day != None):
        query += " AND ah.\"dayofweek\" = " + str(day)
    
        if (time != None):
            query += " AND ah.\"start\" <= \'" + str(time) + "\' AND ah.\"end\" > \'" + str(time) + "\'"
        
    query += " ORDER BY l.\"id\", d.\"id\", dd.\"drinkCategory\""

    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    locations = []
    for row in rows:
        if (len(locations) == 0 or int(row[0]) != locations[len(locations) - 1]["id"]):
            locations.append({ 
                "id": int(row[0]),
                "name": row[1],
                "latitude": float(row[2]), 
                "longitude": float(row[3]),
                "website": row[4], 
                "happyHourWebsite": row[5], 
                "street": row[6], 
                "coverPhotoSource": row[7],
                "coverXOffset": row[8], 
                "coverYOffset": row[9],
                "deals": []
            })
        
        deals = locations[len(locations) - 1]["deals"]
        
        if (len(deals) == 0 or int(row[10]) != deals[len(deals) - 1]["id"]):
            start = None
            if (row[11] != None):
                start = str(row[11])
                
            end = None
            if (row[12] != None):
                end = str(row[12])
                
            deals.append({ 
                "id": int(row[10]),
                "start": start,
                "end": end,
                "dealDetails": []
            })
        
        deals[len(deals) - 1]["dealDetails"].append({
            "drinkName": row[13],
            "drinkCategory": row[14],
            "detailType": row[15],
            "value": row[16]
        })     

    return JsonResponse({ "result": json.dumps(locations) })

def fetch_location_counts_by_neighborhood(request):
    time = request.GET.get('time')
    day = request.GET.get('day')
    
    # Select locations with optional day and time filters
    inner_query = "SELECT * FROM \"vp_location\""
    if (day != None):
        inner_query = "SELECT DISTINCT(l.*) FROM \"vp_location\" l \
            JOIN \"vp_location_deals\" ld \
        	ON l.\"id\" = ld.\"location_id\" \
        	JOIN \"vp_deal\" d \
        	ON d.\"id\" = ld.\"deal_id\" \
        	JOIN \"vp_deal_activeHours\" dah \
        	ON d.\"id\" = dah.\"deal_id\" \
        	JOIN \"vp_activehour\" ah \
        	ON ah.\"id\" = dah.\"activehour_id\" \
        	WHERE ah.\"dayofweek\" = " + str(day)
        
        if (time != None):
            inner_query += " AND ah.\"start\" <= \'" + str(time) + "\' AND ah.\"end\" > \'" + str(time) + "\'"
    
    query = "SELECT ld.neighborhood, count(*) AS count \
        FROM (" + inner_query + ") ld \
        GROUP BY ld.\"neighborhood\""
    
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    result = {}
    for row in rows:
        result[str(row[0])] = int(row[1])

    return JsonResponse({ "result": json.dumps(result) })


def fetch_locations(request):
    time = request.GET.get('time')
    day = request.GET.get('day')
    if(time == None):
        locations = Location.objects.filter(Q(deals__activeHours__dayofweek=day)).distinct().prefetch_related('deals__dealDetails')
    else:
        locations = Location.objects.filter(Q(deals__activeHours__dayofweek=day), Q(deals__activeHours__start__lte=time), Q(deals__activeHours__end__gt=time) | Q(deals__activeHours__end__lte=F('deals__activeHours__start'))).distinct().prefetch_related('deals__dealDetails')
    neighborhoods = locations.values('neighborhood').annotate(total=Count('neighborhood'))
    neighborhooddata = []
    for nh in neighborhoods:
        neighborhood={"neighborhood" : nh.get('neighborhood'), "count" : nh.get('total')}
        neighborhooddata.append(neighborhood)
    container = []
    barLocations = []
    dealInfo = {}
    for location in locations:
        dealList = []
        dealSet = location.deals.filter(Q(dealSource = 1) & Q(confirmed = True))
        if(time == None): 
            dealSet = dealSet.filter(Q(activeHours__dayofweek=day)).all()
        else:
            dealSet = dealSet.filter(Q(activeHours__dayofweek=day), Q(activeHours__start__lte=time), Q(activeHours__end__gt=time) | Q(activeHours__end__lte=F('activeHours__start'))).all()
        superCat=location.locationCategories.filter(isBaseCategory = True).all()[0]
        subCategories = list(location.locationCategories.filter(isBaseCategory = False).values_list('name', flat=True).all())
        beers = []
        wines =[]
        liquors =[]
        for d in dealSet:
            dealDetails = d.dealDetails.all()
            details = {}
            activehours = d.activeHours.all()
          
            for dd in dealDetails:
                if dd.drinkCategory == 1:
                    beer = {"detail_id":dd.id,
                          "drinkName": dd.drinkName,
                          "detailType":dd.detailType,
                          "value":dd.value}
                    beers.append(beer)
                elif dd.drinkCategory == 2:
                    wine = {"detail_id":dd.id,
                          "drinkName": dd.drinkName,
                          "detailType":dd.detailType,
                          "value":dd.value}
                    wines.append(wine)
                elif dd.drinkCategory == 3:
                    liquor = {"detail_id":dd.id,
                          "drinkName": dd.drinkName,
                          "detailType":dd.detailType,
                          "value":dd.value}
                    liquors.append(liquor)
            orderedDetails = (("beer", beers),("wine", wines),("liquor",liquors))
            details = collections.OrderedDict(orderedDetails)
            deals = {"deal_id" : d.id,
                    "details": details }
            for ah in activehours:
                activehour = {"start" : ah.start,
                    "end": ah.end }
                deals["hours"] = activehour
            dealList = deals
        dealData = dealList
        dealInfo[location.id] = dealData
        addressCityIndex = location.formattedAddress.find("Washington,")
        abbreviatedAddress = location.formattedAddress[:addressCityIndex]
        locationData = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [location.longitude, location.latitude]
            },
            "properties": {
                "locationid": location.id,
                "name": location.name,
                "website":location.website,
                "happyHourWebsite":location.happyHourWebsite,
                "phone": location.formattedPhoneNumber,
                "fullAddress": location.formattedAddress,
                "abbreviatedAddress": abbreviatedAddress,
                "neighborhood":location.neighborhood,
                "coverPhotoSource": location.coverPhotoSource,
                "coverPhotoXOffset": location.coverXOffset,
                "coverPhotoYOffset": location.coverYOffset,
                "super_category": superCat.name,
                "subCategories": subCategories,
            }
        }
        barLocations.append(locationData)
    return JsonResponse({'json':barLocations, 'deals':dealInfo, 'neighborhoods':neighborhooddata})


def yelp_reviews(request):
    locationID=request.GET.get('loc_id')
    location=Location.objects.filter(id=locationID).all()[0]

    #need to be moved to config
    yelp_consumer_key = "Piz41a8pB1aBdsTg5jkZDw"
    yelp_consumer_secret = "dN8L0GIUtqt0Aq-Go5EMQnaVNjc"
    yelp_token = "QwcesHf454SdQimI92ZVQ8Dhn1HbfHB5"
    yelp_token_secret = "smLN2bEYWxF3Y7ok19BgdJp3590"
    
    yelp_api = YelpAPI(yelp_consumer_key, yelp_consumer_secret, yelp_token, yelp_token_secret)
    api_response = yelp_api.business_query(id=location.yelpId)

    responseJson= {
        "excerpt": api_response['reviews'][0]['excerpt'],
        "username": api_response['reviews'][0]['user']['name'],
        "user_img": api_response['reviews'][0]['user']['image_url'],
        "overall_rating_img": api_response['rating_img_url'],
        "review_count": api_response['review_count'],
        "url": api_response['url']
    }

    return JsonResponse({'response':responseJson})

def sandbox(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('sandbox.html', context)

#def blog(request):
#    context = {}
#    context.update(csrf(request))
#    return render_to_response('blog.html', context)

def index(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('index.html', context)

def TOS(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('TOS.html', context)

def home(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('index.html', context)

# Manual Happy Hour Entry
@login_required(login_url='/login/')
def enter_happy_hour_view(request):
    context = {}
    context.update(csrf(request))

    return render_to_response('enter_happy_hour.html', context)

@login_required(login_url='/login/')
def data_entry(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return enter_happy_hour_view(request)

@login_required(login_url='/login/')
def confirm_drink_name(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return render_to_response("confirm_drink_name.html", context)

def flag_location_as_skipped(request):
    data = json.loads(request.body)
    location_id = data.get('location_id')
    location = Location.objects.get(id=location_id)
    location.data_entry_skipped = True
    location.save()
    return HttpResponse("success")

def get_location_that_needs_happy_hour(request):
    requiresPhone = request.GET.get("requiresPhone") == "true"
    total_count = Location.objects.filter(data_entry_skipped=requiresPhone, neighborhood="Downtown").count()
    locations = Location.objects.filter(data_entry_skipped=requiresPhone, dealDataManuallyReviewed=None, neighborhood="Downtown").order_by('?')

    if locations.count() > 0:
        selected = locations.first()

        response = {
            'total_count': total_count,
            'remaining_count': locations.count(),
            'location_id': selected.id,
            'location_name': selected.name,
            'location_website': selected.website,
            'location_phone_number': selected.formattedPhoneNumber,
            'location_address': selected.formattedAddress
        }
        return JsonResponse(response)

    return JsonResponse({})

def get_deal_that_needs_confirmation(request):
    deals = Deal.objects.filter(confirmed=False)
    deals_count = deals.count()

    if deals_count > 0:
        deal = deals.first()
        deal_details = list(deal.dealDetails.all())

        deal_detail_data = []

        for deal_detail in deal_details:
            mturk_drink_name_options = list(deal_detail.mturkDrinkNameOptions.all())
            mturk_drink_names = []

            for mturk_drink_name_option in mturk_drink_name_options:
                mturk_drink_names.append(mturk_drink_name_option.name)

            deal_detail_data.append({
                'id': deal_detail.id,
                'drink_names': mturk_drink_names
            })

        response = {
            'deals_count': deals_count,
            'deal_id': deal.id,
            'deal_detail_data': deal_detail_data
        }

        return JsonResponse(response)

    return JsonResponse({ 'deals_count': 0 })



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
def submit_drink_names(request):
    data = json.loads(request.body)
    deal_id = int(data.get('dealID'))
    names_selected = data.get('namesSelected')

    deal = Deal.objects.get(id=deal_id)

    for name_selected in names_selected:
        deal_detail_id = int(name_selected.get('dealDetailID'))
        deal_detail = DealDetail.objects.get(id=deal_detail_id)

        # Save the name for the deal detail
        deal_detail.drinkName = name_selected.get('name')
        mturk_drink_name_options = deal_detail.mturkDrinkNameOptions.all()
        deal_detail.mturkDrinkNameOptions.remove()
        mturk_drink_name_options.delete()
        deal_detail.save()

    # Confirm the deal
    deal.confirmed = True
    deal.save()

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

class BlogProxyView(ProxyView):
    upstream = 'https://viceprice.wordpress.com/'

    def dispatch(self, request, path):
        if request.is_secure():
            scheme = 'https://'
        else:
            scheme = 'http://'
        request_abs_path = scheme + request.get_host() + '/blog/'

        response = ProxyView.dispatch(self, request, path)
        response.content = response.content.replace(BlogProxyView.upstream, request_abs_path)
        return response
