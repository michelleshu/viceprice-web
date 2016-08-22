# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0070_auto_20160807_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='mturkDataCollectionAttempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='location',
            name='mturkNoDealData',
            field=models.BooleanField(default=False),
        ),
    ]
