# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='google_places_id',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='open_street_map_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
