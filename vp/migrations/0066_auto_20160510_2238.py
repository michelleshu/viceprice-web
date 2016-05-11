# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0065_auto_20160510_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='localeRequired',
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='usLocaleRequired',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
