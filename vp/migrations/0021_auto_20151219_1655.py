# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0020_mturklocationinfo_data_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='dealDataSource',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='DealDataSource',
        ),
    ]
