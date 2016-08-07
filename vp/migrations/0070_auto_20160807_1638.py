# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0069_auto_20160522_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='formattedAddress',
        ),
        migrations.AddField(
            model_name='location',
            name='business_email',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
