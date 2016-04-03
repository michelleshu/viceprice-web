# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0049_auto_20160401_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='skipped',
            field=models.BooleanField(default=False),
        ),
    ]
