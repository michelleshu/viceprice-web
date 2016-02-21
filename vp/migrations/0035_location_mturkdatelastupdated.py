# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0034_remove_location_mturkdatelastupdated'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 1, 4, 56, tzinfo=utc)),
        ),
    ]
