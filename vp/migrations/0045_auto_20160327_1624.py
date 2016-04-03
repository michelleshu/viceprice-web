# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0044_auto_20160327_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='dealHour',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='activeHours',
        ),
        migrations.AddField(
            model_name='deal',
            name='activeHours',
            field=models.ManyToManyField(to='vp.ActiveHour', null=True),
        ),
    ]
