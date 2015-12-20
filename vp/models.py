from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from pytz import timezone

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

# Information about a deal at a location
class Deal(models.Model):
    dealHour = models.OneToOneField(BusinessHour)
    description = models.CharField(max_length=512)

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
    foursquareDateLastUpdated = models.DateTimeField(null=True)
    mturkLastUpdateStarted = models.DateTimeField(null=True)
    mturkLastUpdateCompleted = models.DateTimeField(null=True)
    mturkLastUpdateCost = models.FloatField(null=True)
    dealDataSource = models.IntegerField(null=True)
    foursquareId = models.CharField(max_length=50, null=True, unique=True)
    deals = models.ManyToManyField(Deal)
    comments = models.CharField(max_length=1000, null=True)

# Track location as it goes through MTurk update process
class MTurkLocationInfo(models.Model):
    foursquare_id = models.CharField(max_length=50, null=False, unique=True)
    name = models.CharField(max_length=256, null=True)
    address = models.CharField(max_length=512, null=True)
    url = models.CharField(max_length=256, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    rating = models.FloatField(null=True)
    url_provided = models.CharField(max_length=256, null=True)
    url_provided_verified = models.BooleanField(default=False)
    url_found = models.BooleanField(default=False)
    get_hh_attempts = models.IntegerField(null=False)
    deals_confirmations = models.IntegerField(null=False)
    stage = models.IntegerField(null=False)
    data_source = models.IntegerField(null=True)
    hit_id = models.CharField(max_length=100, null=True)
    update_started = models.DateTimeField(null=True)
    update_completed = models.DateTimeField(null=True)
    update_cost = models.FloatField(null=False)
    monday_start_time = models.TimeField(null=True)
    monday_end_time = models.TimeField(null=True)
    monday_description = models.CharField(max_length=512, null=True)
    tuesday_start_time = models.TimeField(null=True)
    tuesday_end_time = models.TimeField(null=True)
    tuesday_description = models.CharField(max_length=512, null=True)
    wednesday_start_time = models.TimeField(null=True)
    wednesday_end_time = models.TimeField(null=True)
    wednesday_description = models.CharField(max_length=512, null=True)
    thursday_start_time = models.TimeField(null=True)
    thursday_end_time = models.TimeField(null=True)
    thursday_description = models.CharField(max_length=512, null=True)
    friday_start_time = models.TimeField(null=True)
    friday_end_time = models.TimeField(null=True)
    friday_description = models.CharField(max_length=512, null=True)
    saturday_start_time = models.TimeField(null=True)
    saturday_end_time = models.TimeField(null=True)
    saturday_description = models.CharField(max_length=512, null=True)
    sunday_start_time = models.TimeField(null=True)
    sunday_end_time = models.TimeField(null=True)
    sunday_description = models.CharField(max_length=512, null=True)
    comments = models.CharField(max_length=1000, null=True)