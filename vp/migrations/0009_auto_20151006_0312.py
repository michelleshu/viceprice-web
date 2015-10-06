# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0008_auto_20151004_1429'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='business_hours',
            new_name='businessHours',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='date_last_updated',
            new_name='dateLastUpdated',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='formatted_address',
            new_name='formattedAddress',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='formatted_phone_number',
            new_name='formattedPhoneNumber',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='foursquare_id',
            new_name='foursquareId',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='location_categories',
            new_name='locationCategories',
        ),
        migrations.RenameField(
            model_name='locationcategory',
            old_name='super_category',
            new_name='superCategory',
        ),
        migrations.RenameField(
            model_name='timeframe',
            old_name='end_time',
            new_name='endTime',
        ),
        migrations.RenameField(
            model_name='timeframe',
            old_name='start_time',
            new_name='startTime',
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='days',
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='time_frames',
        ),
        migrations.AddField(
            model_name='dayofweek',
            name='businessHour',
            field=models.ForeignKey(related_name='days_of_week', to='vp.BusinessHour', null=True),
        ),
        migrations.AddField(
            model_name='timeframe',
            name='businessHour',
            field=models.ForeignKey(related_name='time_frames', to='vp.BusinessHour', null=True),
        ),
    ]
