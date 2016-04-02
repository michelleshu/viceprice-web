# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0050_location_skipped'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dealdetail',
            old_name='type',
            new_name='detailType',
        ),
    ]
