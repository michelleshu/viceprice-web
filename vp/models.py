from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django_enumfield import enum

class LocationCategory(models.Model):
    name = models.CharField(max_length=256, null=False)
    isBaseCategory = models.BooleanField(default=True)
    facebookCategoryId = models.CharField(max_length=256, null=True)
    parentCategory = models.ForeignKey('self', null=True)

class ActiveHour(models.Model):
    dayofweek = models.IntegerField()
    start = models.TimeField(null=True)
    end = models.TimeField(null=True)

# Drink names from deal details entered by MTurk Workers
class MTurkDrinkNameOption(models.Model):
    name = models.CharField(max_length=1000)

# Details about a particular drink and price
class DealDetail(models.Model):
    drinkName = models.CharField(max_length=1000)
    drinkCategory = models.IntegerField()
    detailType = models.IntegerField()
    value = models.FloatField()
    mturkDrinkNameOptions = models.ManyToManyField(MTurkDrinkNameOption)

# Information about a deal at a location
class Deal(models.Model):
    activeHours = models.ManyToManyField(ActiveHour)
    dealDetails = models.ManyToManyField(DealDetail)
    comments = models.CharField(null=True, max_length=2000)
    confirmed = models.BooleanField(default=True)
    confirmedDate = models.DateTimeField(null=True)

# Information about a location
class Location(models.Model):
    name = models.CharField(max_length=256, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    locationCategories = models.ManyToManyField(LocationCategory)
    activeHours = models.ManyToManyField(ActiveHour)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=50, null=True)
    street = models.CharField(max_length=256, null=True)
    zip = models.CharField(max_length=50, null=True)
    formattedPhoneNumber = models.CharField(max_length=30, null=True)
    website = models.CharField(max_length=256, null=True)
    happyHourWebsite = models.CharField(max_length=512, null=True)
    coverPhotoSource = models.CharField(max_length=256, null=True)
    coverXOffset = models.IntegerField(null=True)
    coverYOffset = models.IntegerField(null=True)
    deals = models.ManyToManyField(Deal, related_name="location")
    dateLastUpdated = models.DateTimeField(null=True)
    lastUpdatedBy = models.CharField(max_length=64, null=True)
    mturkNoDealData = models.BooleanField(null=False, default=False)
    mturkDataCollectionFailed = models.BooleanField(null=False, default=False)
    mturkDataCollectionAttempts = models.IntegerField(null=False, default=0)
    facebookId = models.CharField(max_length=50, null=True)
    foursquareId = models.CharField(max_length=50, null=True)
    twitterHandle = models.CharField(max_length=50, null=True)
    yelpId = models.CharField(max_length=50, null=True)
    neighborhood=models.CharField(max_length=256, null=True)
    businessEmail = models.CharField(max_length=256, null=True)

# Track the time and cost of MTurk stage
class MTurkLocationInfoStat(models.Model):
    location = models.ForeignKey(Location)
    dateStarted = models.DateTimeField(null=False)
    dateCompleted = models.DateTimeField(null=True)
    numberOfAssignments = models.IntegerField(null=False)
    costPerAssignment = models.FloatField(null=False)

    # Attempts and confirmation settings (found in settings.py)
    minAgreementPercentage = models.IntegerField(null=False)

    # MTurk Qualification Configuration (found in settings.py)
    minPercentagePreviousAssignmentsApproved = models.IntegerField(null=False)
    minHITsCompleted = models.IntegerField(null=False)
    localeRequired = models.CharField(null=True, max_length=3)

    happyHourDataFound = models.BooleanField(default=False)


# Track location as it goes through MTurk update process
class MTurkLocationInfo(models.Model):
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=256, null=True)
    address = models.CharField(max_length=512, null=True)
    website = models.CharField(max_length=512, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    hit_id = models.CharField(max_length=100, null=True)
    comments = models.CharField(max_length=1000, null=True)
    stat = models.ForeignKey(MTurkLocationInfoStat, null=True)