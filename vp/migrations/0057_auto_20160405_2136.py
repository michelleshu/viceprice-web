# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0056_auto_20160405_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='zip',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
