# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0033_auto_20160221_1337'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='mturkDateLastUpdated',
        ),
    ]
