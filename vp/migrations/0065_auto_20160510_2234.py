# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0064_auto_20160508_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='usLocaleRequired',
        ),
        migrations.AddField(
            model_name='mturklocationinfostat',
            name='localeRequired',
            field=models.CharField(max_length=3, null=True),
        ),
    ]
