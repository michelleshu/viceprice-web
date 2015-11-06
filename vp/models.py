from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from pytz import timezone
import pytz

DAY_OF_WEEK = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7
}

EASTERN_TIMEZONE = timezone('US/Eastern')

class LocationCategory(models.Model):
    name = models.CharField(max_length=256, null=False)
    superCategory = models.ForeignKey('self', null=True)

# A BusinessHour is a combination of days of week and open time frames for those days
class BusinessHourManager(models.Manager):
    def create(self, time_frames_data, days_of_week):
        business_hour = BusinessHour()
        business_hour.save()

        for tf in time_frames_data:
            # Convert times from military time strings to time objects
            start_time = EASTERN_TIMEZONE.localize(datetime.strptime(tf['start'][-4:], '%H%M'))
            end_time = EASTERN_TIMEZONE.localize(datetime.strptime(tf['end'][-4:], '%H%M'))

            time_frame = TimeFrame(startTime = start_time, endTime = end_time, businessHour = business_hour)
            time_frame.save()

        for d in days_of_week:
            d = DayOfWeek(day = d, businessHour = business_hour)
            d.save()

        return business_hour

class BusinessHour(models.Model):
    objects = BusinessHourManager()

class DayOfWeek(models.Model):
    day = models.IntegerField()
    businessHour = models.ForeignKey(BusinessHour, related_name='days_of_week', null=True)

class TimeFrame(models.Model):
    startTime = models.TimeField()
    endTime = models.TimeField()
    businessHour = models.ForeignKey(BusinessHour, related_name='time_frames', null=True)

# Information about a location
class Location(models.Model):
    name = models.CharField(max_length=256, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    locationCategories = models.ManyToManyField(LocationCategory)
    businessHours = models.ManyToManyField(BusinessHour)
    formattedAddress = models.CharField(max_length=512, null=True)
    formattedPhoneNumber = models.CharField(max_length=30, null=True)
    website = models.CharField(max_length=256, null=True)
    rating = models.FloatField(null=True)
    dateLastUpdated = models.DateTimeField(auto_now_add=True, null=True)
    foursquareId = models.CharField(max_length=50, null=True, unique=True)