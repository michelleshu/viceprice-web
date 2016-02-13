# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0027_auto_20160123_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='data_source',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='update_completed',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='update_cost',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='update_started',
        ),
        migrations.AddField(
            model_name='mturklocationinfo',
            name='attempts',
            field=models.IntegerField(default=0),
        ),
    ]
