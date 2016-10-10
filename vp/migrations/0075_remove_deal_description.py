# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0074_auto_20161002_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='description',
        ),
    ]
