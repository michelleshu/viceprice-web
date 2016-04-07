# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0054_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationcategory',
            old_name='superCategory',
            new_name='parentCategory',
        ),
        migrations.AddField(
            model_name='locationcategory',
            name='facebookCategoryId',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='locationcategory',
            name='isBaseCategory',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='dealdetail',
            name='detailType',
            field=models.IntegerField(),
        ),
    ]
