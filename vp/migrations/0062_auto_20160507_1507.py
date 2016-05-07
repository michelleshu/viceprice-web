# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0061_auto_20160501_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTurkDrinkNameOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000)),
            ],
        ),
        migrations.AddField(
            model_name='deal',
            name='confirmed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='dealdetail',
            name='mturkDrinkNameOptions',
            field=models.ManyToManyField(to='vp.MTurkDrinkNameOption'),
        ),
    ]
