# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0057_auto_20160405_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturklocationinfostat',
            old_name='costPerAssignment',
            new_name='cost',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfo',
            name='stage',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='costForStage',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='dataConfirmed',
        ),
        migrations.RemoveField(
            model_name='mturklocationinfostat',
            name='stage',
        ),
        migrations.AddField(
            model_name='deal',
            name='dealSource',
            field=models.IntegerField(default=1),
        ),
    ]
