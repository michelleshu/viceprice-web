# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0013_auto_20151129_1919'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='dateLastUpdated',
        ),
        migrations.AddField(
            model_name='location',
            name='foursquareDateLastUpdated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(null=True),
        ),
    ]
