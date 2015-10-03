# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0005_location_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationcategory',
            name='super_category',
            field=models.ForeignKey(to='vp.LocationCategory', null=True),
        ),
    ]
