# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0016_auto_20151206_1842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='check_ins',
            new_name='checkIns',
        ),
    ]
