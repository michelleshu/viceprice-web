# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0059_auto_20160420_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='happyHourDataFound',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='minHITsCompleted',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='minPercentagePreviousAssignmentsApproved',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
