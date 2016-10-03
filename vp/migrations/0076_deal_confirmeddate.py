# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0075_remove_deal_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='confirmedDate',
            field=models.DateTimeField(null=True),
        ),
    ]
