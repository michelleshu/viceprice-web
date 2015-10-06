# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0007_auto_20151003_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayOfWeek',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TimeFrame',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='closing_time',
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='day_of_week',
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='opening_time',
        ),
        migrations.RemoveField(
            model_name='location',
            name='description',
        ),
        migrations.AddField(
            model_name='businesshour',
            name='days',
            field=models.ManyToManyField(to='vp.DayOfWeek'),
        ),
        migrations.AddField(
            model_name='businesshour',
            name='time_frames',
            field=models.ManyToManyField(to='vp.TimeFrame'),
        ),
    ]
