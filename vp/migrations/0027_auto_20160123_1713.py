# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0026_auto_20160123_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mturklocationinfo',
            name='update_cost',
            field=models.FloatField(default=0.0),
        ),
    ]
