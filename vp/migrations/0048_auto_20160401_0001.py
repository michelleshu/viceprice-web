# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0047_auto_20160331_2329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='dealDetails',
        ),
        migrations.AddField(
            model_name='dealdetail',
            name='deal',
            field=models.ForeignKey(default=1, to='vp.Deal'),
            preserve_default=False,
        ),
    ]
