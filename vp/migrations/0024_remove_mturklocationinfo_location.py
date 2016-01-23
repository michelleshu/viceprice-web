# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0023_auto_20160123_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='location',
        ),
    ]
