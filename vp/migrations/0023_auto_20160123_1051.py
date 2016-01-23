# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0022_auto_20160123_1041'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturklocationinfo',
            old_name='location_id',
            new_name='location',
        )
    ]
