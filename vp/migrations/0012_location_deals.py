# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0011_deal'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='deals',
            field=models.ManyToManyField(to='vp.Deal'),
        ),
    ]
