# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0032_auto_20160221_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 1, 0, 0)),
        ),
    ]
