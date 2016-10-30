from django.core.management.base import BaseCommand
from vp.models import Location
from viceprice import settings
import datetime
import json

class Command(BaseCommand):
    
    def export_location_data(self):        
        locations = Location.objects.all()
        locations_output = []
        
        for location in locations:    
            location_object = {
                'name': location.name,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'website': location.website,
                'happyHourWebsite': location.happyHourWebsite,
                'phoneNumber': location.formattedPhoneNumber,
                'businessEmail': location.businessEmail,
                'neighborhood': location.neighborhood,
                'facebookId': location.facebookId,
                'yelpId': location.yelpId
            }
            
            if (location.street != None):
                location_object['address'] = {
                    'street': location.street,
                    'city': location.city,
                    'state': location.state,
                    'zip': location.zip
                }
            
            location_categories = location.locationCategories.filter(isBaseCategory = False).all()
            
            if (len(location_categories) > 0):
                location_object['locationCategories'] = []
            
                for location_category in location_categories:
                    location_object['locationCategories'].append(location_category.name)
                
            business_hours = location.activeHours.all()
            
            if (len(business_hours) > 0):
                location_object['businessHours'] = []
                
                for business_hour in business_hours:
                    location_object['businessHours'].append({
                        'day': business_hour.dayofweek,
                        'openingTime': business_hour.start.strftime('%H:%M'),
                        'closingTime': business_hour.end.strftime('%H:%M')
                    })
                    
            location_deals = location.deals.all()
            
            if (len(location_deals) > 0):
                location_object['deals'] = []
                
                for deal in location_deals:
                    
                    deal_details = deal.dealDetails.all()
                    
                    for active_hour in deal.activeHours.all():
                        
                        deal = {
                            'day': active_hour.dayofweek,
                            'startTime': active_hour.start.strftime('%H:%M'),
                            'details': []
                        }
                        
                        if (active_hour.end != None):
                            deal['endTime'] = active_hour.end.strftime('%H:%M')
                        
                        for deal_detail in deal_details:
                            
                            drinkCategory = None
                            if (deal_detail.drinkCategory == 1):
                                drinkCategory = 'Beer'
                            elif (deal_detail.drinkCategory == 2):
                                drinkCategory = 'Wine'
                            elif (deal_detail.drinkCategory == 3):
                                drinkCategory = 'Liquor'
                                
                            detailType = None
                            if (deal_detail.detailType == 1):
                                detailType = 'Price'
                            elif (deal_detail.detailType == 2):
                                detailType = 'Percent Off'
                            elif (deal_detail.detailType == 3):
                                detailType = 'Price Off'
                            
                            deal['details'].append({
                                'drinkName': deal_detail.drinkName,
                                'drinkCategory': drinkCategory,
                                'dealType': detailType,
                                'dealValue': deal_detail.value
                            })
                            
                        location_object['deals'].append(deal)
            
            if (not location.mturkDataCollectionFailed and not location.mturkNoDealData and location.dateLastUpdated != None):
                location_object['lastUpdatedAt'] = location.dateLastUpdated.isoformat()
            else:
                location_object['lastUpdatedAt'] = None
                
            locations_output.append(location_object)
            print(location_object['name'])
            
        with open('dump.json', 'w') as outfile:
            json.dump(locations_output, outfile, indent=2)
            
        outfile.close()
        
    def handle(self, *args, **options):
        self.export_location_data()