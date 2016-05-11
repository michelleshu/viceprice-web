# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0066_auto_20160510_2238'),
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
