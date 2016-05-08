# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0062_auto_20160507_1507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='maxGetHappyHourAttempts',
        ),
    ]
