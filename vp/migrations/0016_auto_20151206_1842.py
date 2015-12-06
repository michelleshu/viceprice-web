# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0015_auto_20151201_0119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='mturkDateLastUpdated',
            new_name='mturkLastUpdateCompleted',
        ),
        migrations.AddField(
            model_name='location',
            name='mturkLastUpdateCost',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='mturkLastUpdateStarted',
            field=models.DateTimeField(null=True),
        ),
    ]
