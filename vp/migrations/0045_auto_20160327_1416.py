# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0044_location_neighborhood'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(null=True),
        ),
    ]
