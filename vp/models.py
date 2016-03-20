from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

MONDAY = 'Monday'
TUESDAY = 'Tuesday'
WEDNESDAY = 'Wednesday'
THURSDAY = 'Thursday'
FRIDAY = 'Friday'
SATURDAY = 'Saturday'
SUNDAY = 'Sunday'

DAY_OF_WEEK = {
    MONDAY: 1,
    TUESDAY: 2,
    WEDNESDAY: 3,
    THURSDAY: 4,
    FRIDAY: 5,
    SATURDAY: 6,
    SUNDAY: 7
}

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
            start_time = tf['start']
            end_time = tf['end']

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

# Information about a deal at a location
class Deal(models.Model):
    dealHour = models.OneToOneField(BusinessHour)
    description = models.CharField(max_length=2000)

# Details about a particular drink and price
class DealDetail(models.Model):
    deal = models.ForeignKey(Deal)
    drinkName = models.CharField(max_length=1000)
    drinkCategory = models.IntegerField()
    type = models.IntegerField()
    value = models.FloatField()

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
    dealDataSource = models.IntegerField(null=True)
    deals = models.ManyToManyField(Deal)
    mturkDateLastUpdated = models.DateTimeField(default=timezone.make_aware(datetime(year=2016, month=1, day=1), timezone.get_current_timezone()))
    comments = models.CharField(max_length=1000, null=True)
    facebookId = models.CharField(max_length=50, null=True)
    foursquareId = models.CharField(max_length=50, null=True)
    twitterHandle = models.CharField(max_length=50, null=True)
    yelpId = models.CharField(max_length=50, null=True)

# Track the time and cost of MTurk stage
class MTurkLocationInfoStat(models.Model):
    location = models.ForeignKey(Location)
    dateStarted = models.DateTimeField(null=False)
    dateCompleted = models.DateTimeField(null=True)
    stage = models.IntegerField(null=False)
    costPerAssignment = models.FloatField(null=False)
    costForStage = models.FloatField(default=0.0)
    dataConfirmed = models.BooleanField(default=False)

# Track location as it goes through MTurk update process
class MTurkLocationInfo(models.Model):
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=256, null=True)
    address = models.CharField(max_length=512, null=True)
    website = models.CharField(max_length=256, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    stage = models.IntegerField(null=False)
    attempts = models.IntegerField(default=0)
    confirmations = models.IntegerField(default=0)
    deals = models.CharField(max_length=10000, null=True)
    hit_id = models.CharField(max_length=100, null=True)
    comments = models.CharField(max_length=1000, null=True)
    stat = models.ForeignKey(MTurkLocationInfoStat, null=True)