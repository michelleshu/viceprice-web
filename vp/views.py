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
from models import Location, LocationCategory, Deal, DealDetail, ActiveHour, MTurkLocationInfo
from viceprice import settings
from revproxy.views import ProxyView
import json
import logging
import collections
from yelpapi import YelpAPI
import datetime

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
    yesterday = int(day) - 1
    if (yesterday == 0):
        yesterday = 7

    location_query = "SELECT l.\"id\", l.\"name\", l.\"latitude\", l.\"longitude\", l.\"website\", l.\"happyHourWebsite\", l.\"formattedPhoneNumber\", \
        l.\"street\", l.\"coverPhotoSource\", l.\"coverXOffset\", l.\"coverYOffset\", l.\"yelpId\", \
        d.\"id\", ah.\"start\", ah.\"end\", dd.\"drinkName\", dd.\"drinkCategory\", dd.\"detailType\", dd.\"value\", ah.\"dayofweek\" \
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
        WHERE l.\"neighborhood\" = \'" + str(neighborhood) + "\'"

    if (day != None):
        if (time == None):
            location_query += " AND ah.\"dayofweek\" = " + str(day)
        else:
            location_query += " AND ( " + \
                "(ah.\"end\" IS NOT NULL AND ah.\"start\" < ah.\"end\" AND ah.\"dayofweek\" = " + str(day) + \
                " AND ah.\"start\" <= \'" + str(time) + "\' AND ah.\"end\" > \'" + str(time) + "\')" + \
                " OR (ah.\"end\" IS NOT NULL AND ah.\"end\" < ah.\"start\" AND \
                    (ah.\"dayofweek\" = " + str(yesterday) + " AND ah.\"end\" > \'" + str(time) + "\' \
                    OR ah.\"dayofweek\" = " + str(day) + " AND ah.\"start\" <= \'" + str(time) + "\')))"
        
    location_query += " ORDER BY l.\"id\", d.\"id\", dd.\"drinkName\""

    cursor = connection.cursor()
    cursor.execute(location_query)
    rows = cursor.fetchall()
    
    locations = []
    location_ids = []
    for row in rows:
        if (len(locations) == 0 or int(row[0]) != locations[len(locations) - 1]["properties"]["id"]):
            locations.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row[3]), float(row[2])]
                },
                "properties": {
                    "id": int(row[0]),
                    "name": row[1],
                    "latitude": float(row[2]), 
                    "longitude": float(row[3]),
                    "website": row[4], 
                    "happyHourWebsite": row[5],
                    "phoneNumber": row[6], 
                    "street": row[7], 
                    "coverPhotoSource": row[8],
                    "coverXOffset": row[9], 
                    "coverYOffset": row[10],
                    "yelpId": row[11],
                    "deals": []
                }
            })
            location_ids.append(str(row[0]))
        
        deals = locations[len(locations) - 1]["properties"]["deals"]
        
        if (len(deals) == 0 or int(row[12]) != deals[len(deals) - 1]["id"]):
            start = None
            if (row[13] != None):
                start = str(row[13])
                
            end = None
            if (row[14] != None):
                end = str(row[14])
                
            deals.append({ 
                "id": int(row[12]),
                "start": start,
                "end": end,
                "day": int(row[19]),
                "dealDetails": []
            })
        
        deal_details = deals[len(deals) - 1]["dealDetails"]
        if (len(deal_details) == 0 or row[15] != deal_details[len(deal_details) - 1]["drinkName"]):
            deal_details.append({
                "drinkName": row[15],
                "drinkCategory": row[16],
                "detailType": row[17],
                "value": row[18]
            })

    if (len(location_ids) > 0):
        # Execute query for location categories
        location_categories_query = "SELECT llc.\"location_id\", lc.\"name\" \
            FROM \"vp_location_locationCategories\" llc \
            JOIN \"vp_locationcategory\" lc \
            ON llc.\"locationcategory_id\" = lc.\"id\" \
            WHERE llc.\"location_id\" IN (" + ",".join(location_ids) + ") \
            ORDER BY llc.\"location_id\", lc.\"isBaseCategory\" DESC"
            
        cursor.execute(location_categories_query)
        rows = cursor.fetchall()
        categories = {}
        for row in rows:
            if (row[0] not in categories):
                categories[row[0]] = {
                    "base_category": row[1],
                    "sub_categories": []
                }
            else:
                categories[row[0]]["sub_categories"].append(row[1])
                
        for location in locations:
            location_id = location["properties"]["id"]
            if location_id in categories:
                location["properties"]["superCategory"] = categories[location_id]["base_category"]
                location["properties"]["subCategories"] = categories[location_id]["sub_categories"]
    
    return JsonResponse({ 
        "result": json.dumps({
            "type": "FeatureCollection",
            "features": locations 
        })
    })

def fetch_location_counts_by_neighborhood(request):
    time = request.GET.get('time')
    day = request.GET.get('day')
    
    yesterday = int(day) - 1
    if (yesterday == 0):
        yesterday = 7
    
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
        	ON ah.\"id\" = dah.\"activehour_id\" "
        
        if (time == None):
            inner_query += "WHERE ah.\"dayofweek\" = " + str(day)
        else:
            inner_query += "WHERE (" + \
                "(ah.\"end\" IS NOT NULL AND ah.\"start\" < ah.\"end\" AND ah.\"dayofweek\" = " + str(day) + \
                " AND ah.\"start\" <= \'" + str(time) + "\' AND ah.\"end\" > \'" + str(time) + "\')" + \
                " OR (ah.\"end\" IS NOT NULL AND ah.\"end\" < ah.\"start\" AND \
                    (ah.\"dayofweek\" = " + str(yesterday) + " AND ah.\"end\" > \'" + str(time) + "\' \
                    OR ah.\"dayofweek\" = " + str(day) + " AND ah.\"start\" <= \'" + str(time) + "\')))"
    
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

def yelp_reviews(request):
    yelpId = request.GET.get('yelp_id')
    
    yelp_api = YelpAPI(
        settings.YELP_CONSUMER_KEY,
        settings.YELP_CONSUMER_SECRET,
        settings.YELP_TOKEN,
        settings.YELP_TOKEN_SECRET
    )
    api_response = yelp_api.business_query(id = yelpId)

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
def location_list_view(request, sort):
    sort_by = 'neighborhood'
    if (len(sort) > 0 and sort != 'deals' and sort != 'status'):
        sort_by = sort
    
    locations = Location.objects.prefetch_related('deals').order_by(sort_by).all()
    mturkLocations = MTurkLocationInfo.objects.values_list('location_id', flat=True).all()
    
    locations_data = []
    
    in_progress = 0
    passed = 0
    no_deal_data = 0
    data_collection_failed = 0
    no_website = 0
    
    status = None
    for location in locations:
        mturkInProgress = location.id in mturkLocations
        if (mturkInProgress):
            in_progress += 1
            status = 1
        elif (location.happyHourWebsite == None or location.happyHourWebsite == ''):
            no_website += 1
            status = 5
        elif (location.mturkNoDealData):
            no_deal_data += 1
            status = 4
        elif (location.mturkDataCollectionFailed):
            data_collection_failed += 1
            status = 3
        else:
            passed += 1
            status = 2
        
        lastUpdated = None
        if (location.dateLastUpdated != None):
            lastUpdated = location.dateLastUpdated.strftime('%m/%d')
        
        location_data = {
            'id': location.id,
            'name': location.name,
            'neighborhood': location.neighborhood,
            'happyHourWebsite': location.happyHourWebsite,
            'businessEmail': location.businessEmail,
            'mturkNoDealData': location.mturkNoDealData,
            'mturkDataCollectionFailed': location.mturkDataCollectionFailed,
            'mturkInProgress': mturkInProgress,
            'lastUpdated': lastUpdated,
            'lastUpdatedBy': location.lastUpdatedBy,
            'dealCount': len(location.deals.all()),
            'status': status
        }
        locations_data.append(location_data)
    
    if (sort == 'deals'):
        locations_data = sorted(locations_data, key=lambda location: location["dealCount"])
    
    if (sort == 'status'):
        locations_data = sorted(locations_data, key=lambda location:location["status"])
    
    context = {
        'locations': locations_data,
        'passed': passed,
        'noDealData': no_deal_data,
        'dataCollectionFailed': data_collection_failed,
        'noWebsite': no_website,
        'inProgress': in_progress
    }
    context.update(csrf(request))
    
    return render_to_response('location_list.html', context)

@login_required(login_url='/login/')
def enter_happy_hour_view(request, id):
    location = Location.objects.prefetch_related('deals').get(id=id)
    location_deals = location.deals.filter(confirmed=True).all()
    
    deals = []
    
    for location_deal in location_deals:
        deals.append({
            'id': location_deal.id,
            'activeHours': location_deal.activeHours.order_by('dayofweek').all(),
            'dealDetails': location_deal.dealDetails.order_by('drinkCategory').all()
        })
    
    context = {
        'location': location,
        'deals': deals,
        'userFirstName': request.user.first_name
    }
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
            'location_address': selected.street
        }
        return JsonResponse(response)

    return JsonResponse({})

def get_deal_that_needs_confirmation(request):
    deals = Deal.objects.filter(confirmed=False)
    deals_count = deals.count()

    if deals_count > 0:
        deal = deals.first()
        location = deal.location.all().first()

        deal_hours = deal.activeHours.all()

        deal_hour_data = []

        for deal_hour in deal_hours:
            deal_hour_data.append({
                'day': deal_hour.dayofweek,
                'start': str(deal_hour.start),
                'end': str(deal_hour.end)
            })

        deal_details = list(deal.dealDetails.all())

        deal_detail_data = []

        for deal_detail in deal_details:

            mturk_drink_name_options = list(deal_detail.mturkDrinkNameOptions.all())
            mturk_drink_names = []

            for mturk_drink_name_option in mturk_drink_name_options:
                mturk_drink_names.append(mturk_drink_name_option.name)

            deal_detail_data.append({
                'id': deal_detail.id,
                'drink_names': mturk_drink_names,
                'detail_type': deal_detail.detailType,
                'drink_category': deal_detail.drinkCategory,
                'value': deal_detail.value
            })

        response = {
            'location_id': location.id,
            'location_name': location.name,
            'deals_count': deals_count,
            'deal_id': deal.id,
            'deal_hour_data': deal_hour_data,
            'deal_detail_data': deal_detail_data
        }

        return JsonResponse(response)

    return JsonResponse({ 'deals_count': 0 })
    
@csrf_exempt
def delete_deal(request):
    data = json.loads(request.body)
    deal_id = data.get('id')
    
    if (deal_id != None):
        deal = Deal.objects.get(id = deal_id)
        deal.activeHours.all().delete()
        deal.dealDetails.all().delete()
        deal.delete()
        
    return HttpResponse("success")

@csrf_exempt
def delete_deal_detail(request):
    data = json.loads(request.body)
    deal_detail_id = data.get('id')

    if (deal_detail_id != None):
        DealDetail.objects.get(id = deal_detail_id).delete()
    return HttpResponse("success")

@csrf_exempt
def reject_deals(request):
    data = json.loads(request.body)
    location_id = data.get('locationID')

    try:
        location = Location.objects.get(id = location_id)
        location.deals.filter(confirmed = False).delete()

        location.mturkDataCollectionFailed = True
        location.mturkDataCollectionAttempts = 0
        location.dateLastUpdated = datetime.datetime.now() + datetime.timedelta(-31)
        location.save()

    except:
        pass

    return HttpResponse("success")

def add_deal(request):
    data = json.loads(request.body)
    
    DRINK_CATEGORIES = {
        'beer': 1,
        'wine': 2,
        'liquor': 3
    }
    
    DEAL_TYPES = {
        'price': 1,
        'percent-off': 2,
        'price-off': 3
    }
    
    location_id = data.get('location_id')
    
    location = Location.objects.get(id=location_id)
    deal_data = data.get('deal')
    deal = Deal()
    deal.save()
    
    for day in deal_data.get('daysOfWeek'):        
        for tp_data in deal_data.get('timePeriods'):
            # push the time periods to the time_periods array
            activeHour = ActiveHour()
            activeHour.dayofweek = day
            activeHour.start = tp_data.get("startTime")
            activeHour.end = tp_data.get("endTime")
            
            if activeHour.end == "":
                activeHour.end = None
                
            activeHour.save()
            deal.activeHours.add(activeHour)
            
    deal_detail_data = deal_data.get('dealDetails')
    for detail in deal_detail_data:
        drink_names = detail.get("names")
        category = DRINK_CATEGORIES[detail.get("category")]
        type = DEAL_TYPES[detail.get("dealType")]
        dealDetail = DealDetail(drinkName=drink_names, drinkCategory=category, detailType=type, value=detail.get("dealValue"))
        
        dealDetail.save()
        deal.dealDetails.add(dealDetail)
        
    location.deals.add(deal)
    location.save()
    
    return HttpResponse('success');
    
def mark_location_updated(request):
    data = json.loads(request.body)
    location_id = int(data.get('location_id'))
    updated_by = data.get('updated_by')
    
    location = Location.objects.get(id=location_id)
    location.dateLastUpdated = datetime.datetime.now()
    location.lastUpdatedBy = updated_by
    location.save()
    
    return HttpResponse('success')

@csrf_exempt
def submit_drink_names(request):
    data = json.loads(request.body)
    location_id = int(data.get('locationID'))
    deal_id = int(data.get('dealID'))
    names_selected = data.get('namesSelected')

    # Remove old deals from location if they exist
    location = Location.objects.get(id=location_id)
    date_cutoff = datetime.datetime.now() + datetime.timedelta(-30)
    location.deals.filter(confirmed=True).filter(confirmedDate__lt=date_cutoff).delete()
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
    deal.confirmedDate = datetime.datetime.now()
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
