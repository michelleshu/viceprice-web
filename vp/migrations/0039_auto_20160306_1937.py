# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0038_auto_20160301_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mturklocationinfostat',
            name='dateCompleted',
            field=models.DateTimeField(null=True),
        ),
    ]