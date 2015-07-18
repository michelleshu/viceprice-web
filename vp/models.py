from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

# A category of product (e.g. cigarettes, beer)
class ProductCategory(models.Model):
    name = models.CharField(max_length=256)

# An opening and closing time of business on a given day
class BusinessHour(models.Model):
    DAYS_OF_WEEK = (
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday')
    )

    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, default='MONDAY')
    opening_time = models.TimeField()
    closing_time = models.TimeField()

# Information about a location
class Location(models.Model):
    name = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=512)
    zip_code = models.IntegerField()
    phone_number = models.CharField(max_length=30)
    website = models.CharField(max_length=256)
    icon = models.CharField(max_length=256)
    product_categories = models.ManyToManyField(ProductCategory)
    business_hours = models.ManyToManyField(BusinessHour)
    google_place_id = models.CharField(max_length=256)
