# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0025_mturklocationinfo_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturklocationinfo',
            old_name='url',
            new_name='website',
        ),
        migrations.RemoveField(
            model_name='location',
            name='rating',
        ),
    ]
