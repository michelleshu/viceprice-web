# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0048_auto_20160401_0001'),
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
    ]
