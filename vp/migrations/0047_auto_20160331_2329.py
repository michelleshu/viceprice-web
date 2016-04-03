# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0046_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealdetail',
            name='deal',
        ),
        migrations.AddField(
            model_name='deal',
            name='dealDetails',
            field=models.ManyToManyField(to='vp.DealDetail'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='activeHours',
            field=models.ManyToManyField(to='vp.ActiveHour'),
        ),
    ]
