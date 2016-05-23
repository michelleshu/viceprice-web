# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0068_location_happyhourwebsite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='deals',
            field=models.ManyToManyField(related_name='location', to='vp.Deal'),
        ),
    ]
