# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0004_auto_20151003_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='rating',
            field=models.FloatField(null=True),
        ),
    ]
