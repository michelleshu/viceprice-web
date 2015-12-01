# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0014_auto_20151130_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealDataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='dealDataSource',
            field=models.OneToOneField(null=True, to='vp.DealDataSource'),
        ),
    ]
