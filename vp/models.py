from django.db import models
from django.contrib.auth.models import User

DAY_OF_WEEK = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

class LocationCategory(models.Model):
    name = models.CharField(max_length=256, null=False)
    super_category = models.ForeignKey('self', null=True)

class BusinessHour(models.Model):
    day_of_week = models.IntegerField(null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

# Information about a location
class Location(models.Model):
    name = models.CharField(max_length=256, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    location_categories = models.ManyToManyField(LocationCategory)
    business_hours = models.ManyToManyField(BusinessHour)
    formatted_address = models.CharField(max_length=512, null=True)
    formatted_phone_number = models.CharField(max_length=30, null=True)
    website = models.CharField(max_length=256, null=True)
    description = models.CharField(max_length=1000, null=True)
    rating = models.FloatField(null=True)
    date_last_updated = models.DateTimeField(auto_now_add=True, null=True)
    foursquare_id = models.CharField(max_length=50, null = True)