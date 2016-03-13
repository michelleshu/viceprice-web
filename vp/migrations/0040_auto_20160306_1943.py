# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0039_auto_20160306_1937'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturklocationinfo',
            old_name='stats',
            new_name='stat',
        ),
    ]