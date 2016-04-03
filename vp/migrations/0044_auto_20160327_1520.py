# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0043_auto_20160324_0046'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveHour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dayofweek', models.IntegerField()),
                ('start', models.TimeField(null=True)),
                ('end', models.TimeField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='deal',
            name='activeHours',
            field=models.ForeignKey(related_name='deal', to='vp.ActiveHour', null=True),
        ),
    ]
