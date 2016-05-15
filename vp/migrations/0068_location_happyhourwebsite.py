# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0067_auto_20160510_2243'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='happyHourWebsite',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
