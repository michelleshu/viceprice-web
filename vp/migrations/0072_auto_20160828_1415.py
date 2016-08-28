# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0071_auto_20160814_1903'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='business_email',
            new_name='businessEmail',
        ),
        migrations.AlterField(
            model_name='location',
            name='happyHourWebsite',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
