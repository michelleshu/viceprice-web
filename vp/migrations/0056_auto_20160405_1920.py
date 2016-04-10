# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0055_auto_20160405_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dayofweek',
            name='businessHour',
        ),
        migrations.RemoveField(
            model_name='timeframe',
            name='businessHour',
        ),
        migrations.RemoveField(
            model_name='location',
            name='businessHours',
        ),
        migrations.AddField(
            model_name='location',
            name='activeHours',
            field=models.ManyToManyField(to='vp.ActiveHour'),
        ),
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='coverPhotoSource',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='coverXOffset',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='coverYOffset',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='state',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='street',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='zip',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.DeleteModel(
            name='BusinessHour',
        ),
        migrations.DeleteModel(
            name='DayOfWeek',
        ),
        migrations.DeleteModel(
            name='TimeFrame',
        ),
    ]
