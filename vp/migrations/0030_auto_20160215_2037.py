# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0029_auto_20160215_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='facebookId',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='foursquareId',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='twitterHandle',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='yelpId',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
