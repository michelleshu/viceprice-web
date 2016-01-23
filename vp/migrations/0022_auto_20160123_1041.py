# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0021_auto_20151219_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='deals_confirmations',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='foursquare_id',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='friday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='friday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='friday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='get_hh_attempts',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='monday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='monday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='monday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='saturday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='saturday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='saturday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='sunday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='sunday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='sunday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='thursday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='thursday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='thursday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='tuesday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='tuesday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='tuesday_start_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='url_found',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='url_provided',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='url_provided_verified',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='wednesday_description',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='wednesday_end_time',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='wednesday_start_time',
        ),
        migrations.AddField(
            model_name='mturklocationinfo',
            name='confirmations',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mturklocationinfo',
            name='location_id',
            field=models.ForeignKey(default=1, to='vp.Location'),
            preserve_default=False,
        ),
    ]
