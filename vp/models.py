from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django_enumfield import enum

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
    isBaseCategory = models.BooleanField(default=True)
    facebookCategoryId = models.CharField(max_length=256, null=True)
    parentCategory = models.ForeignKey('self', null=True)

# A BusinessHour is a combination of days of week and open time frames for those days
class BusinessHourManager(models.Manager):
    def create(self, time_frames_data, days_of_week):
        business_hour = BusinessHour()
        business_hour.save()

        for tf in time_frames_data:
            # Convert times from military time strings to time objects
            start_time = tf['start']
            end_time = tf.get('end')
            until_close = tf.get('until_close')
            if until_close == None:
                until_close = False
            if until_close:
                end_time = None
            time_frame = TimeFrame(startTime = start_time, endTime = end_time, untilClose = until_close, businessHour = business_hour)
            time_frame.save()

        for d in days_of_week:
            d = DayOfWeek(day = d, businessHour = business_hour)
            d.save()

        return business_hour

class BusinessHour(models.Model):
    objects = BusinessHourManager()

class ActiveHour(models.Model):
    dayofweek = models.IntegerField()
    start = models.TimeField(null=True)
    end = models.TimeField(null=True)
    
class DayOfWeek(models.Model):
    day = models.IntegerField()
    businessHour = models.ForeignKey(BusinessHour, related_name='days_of_week', null=True)

class TimeFrame(models.Model):
    startTime = models.TimeField()
    endTime = models.TimeField(null=True)
    untilClose = models.BooleanField(default=False)
    businessHour = models.ForeignKey(BusinessHour, related_name='time_frames', null=True)



class DealType(enum.Enum):
    price = 1
    percent_off = 2
    price_off = 3

# Details about a particular drink and price
class DealDetail(models.Model):
    drinkName = models.CharField(max_length=1000)
    drinkCategory = models.IntegerField()
    detailType = models.IntegerField()
#     detailType = enum.EnumField(DealType, default=DealType.price_off)
    value = models.FloatField()
    
    # Information about a deal at a location
class Deal(models.Model):
#     dealHour = models.OneToOneField(BusinessHour)
    description = models.CharField(max_length=2000)
    activeHours = models.ManyToManyField(ActiveHour)
    dealDetails = models.ManyToManyField(DealDetail)
    

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
    mturkDateLastUpdated = models.DateTimeField(null=True)
    comments = models.CharField(max_length=1000, null=True)
    facebookId = models.CharField(max_length=50, null=True)
    foursquareId = models.CharField(max_length=50, null=True)
    twitterHandle = models.CharField(max_length=50, null=True)
    yelpId = models.CharField(max_length=50, null=True)
    dealDataManuallyReviewed = models.DateTimeField(null=True)
    neighborhood=models.CharField(max_length=256, null=True)
    data_entry_skipped=models.BooleanField(default=False)

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