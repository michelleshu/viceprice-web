# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0060_auto_20160425_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='attempts',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='confirmations',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='deals',
        ),
    ]
