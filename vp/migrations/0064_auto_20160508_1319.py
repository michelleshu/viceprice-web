# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0063_remove_mturklocationinfostat_maxgethappyhourattempts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturklocationinfostat',
            old_name='minConfirmationPercentage',
            new_name='minAgreementPercentage',
        ),
    ]
