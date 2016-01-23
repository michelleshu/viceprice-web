# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0024_remove_mturklocationinfo_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='mturklocationinfo',
            name='location',
            field=models.ForeignKey(default=1, to='vp.Location'),
            preserve_default=False,
        ),
    ]
