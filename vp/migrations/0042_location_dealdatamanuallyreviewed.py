# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0041_dealdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='dealDataManuallyReviewed',
            field=models.DateTimeField(null=True),
        ),
    ]
