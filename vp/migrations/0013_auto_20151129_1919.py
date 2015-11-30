# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0012_location_deals'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deal',
            old_name='businessHour',
            new_name='dealHour',
        ),
        migrations.AddField(
            model_name='location',
            name='check_ins',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='comments',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
