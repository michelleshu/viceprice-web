# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0031_mturklocationinfo_deals'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='foursquareDateLastUpdated',
        ),
        migrations.AddField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(null=True),
        ),
    ]
