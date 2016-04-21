# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0058_auto_20160420_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='location',
            name='dealDataSource',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='cost',
        ),
        migrations.AddField(
            model_name='deal',
            name='comments',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='mturkDataCollectionFailed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='costPerAssignment',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='maxGetHappyHourAttempts',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='minConfirmationPercentage',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='numberOfAssignments',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='usLocaleRequired',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
