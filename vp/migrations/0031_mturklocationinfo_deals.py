# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0030_auto_20160215_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='mturklocationinfo',
            name='deals',
            field=models.CharField(max_length=3000, null=True),
        ),
    ]
