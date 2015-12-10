# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0017_auto_20151206_1938'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='checkIns',
        ),
    ]
