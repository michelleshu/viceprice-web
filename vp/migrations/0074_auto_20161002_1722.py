# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0073_auto_20160828_1525'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='dealDataManuallyReviewed',
            new_name='dateLastUpdated',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='dealSource',
        ),
        migrations.RemoveField(
            model_name='location',
            name='data_entry_skipped',
        ),
        migrations.RemoveField(
            model_name='location',
            name='mturkDateLastUpdated',
        ),
        migrations.AddField(
            model_name='location',
            name='lastUpdatedBy',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
