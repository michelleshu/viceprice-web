# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0051_auto_20160402_1000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='skipped',
            new_name='data_entry_skipped',
        ),
    ]
