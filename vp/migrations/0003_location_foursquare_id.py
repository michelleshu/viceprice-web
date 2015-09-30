# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0002_auto_20150907_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='foursquare_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
