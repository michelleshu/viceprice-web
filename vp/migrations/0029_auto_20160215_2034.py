# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0028_auto_20160213_1459'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='mturkLastUpdateCompleted',
        ),
        migrations.RemoveField(
            model_name='location',
            name='mturkLastUpdateCost',
        ),
        migrations.RemoveField(
            model_name='location',
            name='mturkLastUpdateStarted',
        ),
        migrations.AddField(
            model_name='location',
            name='facebookId',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='twitterHandle',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='yelpId',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
    ]
