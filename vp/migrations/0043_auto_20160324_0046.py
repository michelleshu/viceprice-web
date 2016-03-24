# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0042_location_dealdatamanuallyreviewed'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeframe',
            name='untilClose',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='timeframe',
            name='endTime',
            field=models.TimeField(null=True),
        ),
    ]
