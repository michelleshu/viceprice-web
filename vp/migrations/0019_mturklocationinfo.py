# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0018_remove_location_checkins'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTurkLocationInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('foursquare_id', models.CharField(unique=True, max_length=50)),
                ('name', models.CharField(max_length=256, null=True)),
                ('address', models.CharField(max_length=512, null=True)),
                ('url', models.CharField(max_length=256, null=True)),
                ('phone_number', models.CharField(max_length=30, null=True)),
                ('rating', models.FloatField(null=True)),
                ('url_provided', models.CharField(max_length=256, null=True)),
                ('url_provided_verified', models.BooleanField(default=False)),
                ('url_found', models.BooleanField(default=False)),
                ('get_hh_attempts', models.IntegerField()),
                ('deals_confirmations', models.IntegerField()),
                ('stage', models.IntegerField()),
                ('hit_id', models.CharField(max_length=100, null=True)),
                ('update_started', models.DateTimeField(null=True)),
                ('update_completed', models.DateTimeField(null=True)),
                ('update_cost', models.FloatField()),
                ('monday_start_time', models.TimeField(null=True)),
                ('monday_end_time', models.TimeField(null=True)),
                ('monday_description', models.CharField(max_length=512, null=True)),
                ('tuesday_start_time', models.TimeField(null=True)),
                ('tuesday_end_time', models.TimeField(null=True)),
                ('tuesday_description', models.CharField(max_length=512, null=True)),
                ('wednesday_start_time', models.TimeField(null=True)),
                ('wednesday_end_time', models.TimeField(null=True)),
                ('wednesday_description', models.CharField(max_length=512, null=True)),
                ('thursday_start_time', models.TimeField(null=True)),
                ('thursday_end_time', models.TimeField(null=True)),
                ('thursday_description', models.CharField(max_length=512, null=True)),
                ('friday_start_time', models.TimeField(null=True)),
                ('friday_end_time', models.TimeField(null=True)),
                ('friday_description', models.CharField(max_length=512, null=True)),
                ('saturday_start_time', models.TimeField(null=True)),
                ('saturday_end_time', models.TimeField(null=True)),
                ('saturday_description', models.CharField(max_length=512, null=True)),
                ('sunday_start_time', models.TimeField(null=True)),
                ('sunday_end_time', models.TimeField(null=True)),
                ('sunday_description', models.CharField(max_length=512, null=True)),
                ('comments', models.CharField(max_length=1000, null=True)),
            ],
        ),
    ]
