# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vp', '0003_location_foursquare_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('super_category', models.ForeignKey(to='vp.LocationCategory')),
            ],
        ),
        migrations.RemoveField(
            model_name='locationtype',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='businesshour',
            name='day',
        ),
        migrations.RemoveField(
            model_name='location',
            name='address',
        ),
        migrations.RemoveField(
            model_name='location',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='location',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='location',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='location',
            name='date_approved',
        ),
        migrations.RemoveField(
            model_name='location',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='location',
            name='google_places_id',
        ),
        migrations.RemoveField(
            model_name='location',
            name='location_types',
        ),
        migrations.RemoveField(
            model_name='location',
            name='open_street_map_id',
        ),
        migrations.RemoveField(
            model_name='location',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='location',
            name='product_categories',
        ),
        migrations.AddField(
            model_name='businesshour',
            name='day_of_week',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='date_last_updated',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='description',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='formatted_address',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='formatted_phone_number',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='business_hours',
            field=models.ManyToManyField(to='vp.BusinessHour'),
        ),
        migrations.DeleteModel(
            name='Address',
        ),
        migrations.DeleteModel(
            name='LocationType',
        ),
        migrations.DeleteModel(
            name='ProductCategory',
        ),
        migrations.AddField(
            model_name='location',
            name='location_categories',
            field=models.ManyToManyField(to='vp.LocationCategory'),
        ),
    ]
