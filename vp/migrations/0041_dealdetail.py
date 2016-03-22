# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0040_auto_20160306_1943'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('drinkName', models.CharField(max_length=1000)),
                ('drinkCategory', models.IntegerField()),
                ('type', models.IntegerField()),
                ('value', models.FloatField()),
                ('deal', models.ForeignKey(to='vp.Deal')),
            ],
        ),
    ]
