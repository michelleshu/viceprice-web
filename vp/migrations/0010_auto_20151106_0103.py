# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0009_auto_20151006_0312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='foursquareId',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
    ]
