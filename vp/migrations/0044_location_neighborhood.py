# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0043_auto_20160324_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='neighborhood',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
