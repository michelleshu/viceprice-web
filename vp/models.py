from django.db import models
from django.contrib.auth.models import User

LOCATION_TYPE = (
    # Supertypes
    ('STORE', 'Store'),
    ('BAR', 'Bar'),
    ('RESTAURANT', 'Restaurant'),

    # Store Subtypes

    # Bar Subtypes
    ('IRISH', 'Irish'),
    ('PUB', 'Pub'),
    ('BEER_GARDEN', 'Beer Garden'),
    ('COMEDY_CLUB', 'Comedy Club'),
    ('KARAOKE_CLUB', 'Karaoke Club'),
    ('DRAG', 'Drag'),
    ('SPORTS', 'Sports'),
    ('WINE_BAR', 'Wine Bar'),
    ('DIVE_BAR,', 'Dive Bar'),
    ('SALSA', 'Salsa'),
    ('GAY', 'Gay'),
    ('CLUB_DANCE_BAR', 'Club/Dance'),
    ('HOTEL', 'Hotel'),
    ('TOPLESS', 'Topless')
)

PRODUCT_CATEGORY = (
    ('LIQUOR', 'Liquor'),
    ('BEER', 'Beer'),
    ('CIGARETTES', 'Cigarettes'),
    ('WINE', 'Wine'),
    ('CIGARS', 'Cigars')
)

DAYS_OF_WEEK = (
    ('MONDAY', 'Monday'),
    ('TUESDAY', 'Tuesday'),
    ('WEDNESDAY', 'Wednesday'),
    ('THURSDAY', 'Thursday'),
    ('FRIDAY', 'Friday'),
    ('SATURDAY', 'Saturday'),
    ('SUNDAY', 'Sunday')
)

# Information about a location
class Location(models.Model):
    name = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.OneToOneField(Address)
    phone_number = models.CharField(max_length=30, null=True)
    website = models.CharField(max_length=256, null=True)
    location_types = models.ManyToManyField(LocationType)
    product_categories = models.ManyToManyField(ProductCategory)
    business_hours = models.ManyToManyField(BusinessHour, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.OneToOneField(User)
    date_approved = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_by = models.OneToOneField(User)

# The type of location (e.g. store, bar)
class LocationType(models.Model):
    name = models.CharField(max_length=256, choices=LOCATION_TYPE)
    parent = models.ManyToManyField("self", null=True, blank=True)

# A category of product (e.g. cigarettes, beer)
class ProductCategory(models.Model):
    name = models.CharField(max_length=256, choices=PRODUCT_CATEGORY)

# An opening and closing time of business on a given day
class BusinessHour(models.Model):
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, default='MONDAY')
    opening_time = models.TimeField()
    closing_time = models.TimeField()

# Physical address components
class Address(modpels.Model):
    house_number = models.IntField()
    street = models.CharField(max_length=256)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=30)
    display_address = models.charField(max_length=512)