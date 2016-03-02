# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0037_auto_20160222_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTurkLocationInfoStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dateStarted', models.DateTimeField()),
                ('dateCompleted', models.DateTimeField()),
                ('stage', models.IntegerField()),
                ('costPerAssignment', models.FloatField()),
                ('costForStage', models.FloatField(default=0.0)),
                ('dataConfirmed', models.BooleanField(default=False)),
                ('location', models.ForeignKey(to='vp.Location')),
            ],
        ),
        migrations.AlterField(
            model_name='deal',
            name='description',
            field=models.CharField(max_length=2000),
        ),
        migrations.AddField(
            model_name='mturklocationinfo',
            name='stats',
            field=models.ForeignKey(to='vp.MTurkLocationInfoStat', null=True),
        ),
    ]
