# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0046_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='neighborhood',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='activeHours',
            field=models.ManyToManyField(to='vp.ActiveHour'),
        ),
    ]
