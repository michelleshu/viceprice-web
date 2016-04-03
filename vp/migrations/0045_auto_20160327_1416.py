# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    operations = [
        migrations.AlterField(
            model_name='location',
            name='mturkDateLastUpdated',
            field=models.DateTimeField(null=True),
        ),
    ]
