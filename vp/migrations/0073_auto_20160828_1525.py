# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0072_auto_20160828_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mturklocationinfo',
            name='website',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
