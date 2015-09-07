# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('house_number', models.CharField(max_length=10, null=True)),
                ('street', models.CharField(max_length=256, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=30, null=True)),
                ('postal_code', models.CharField(max_length=30, null=True)),
                ('display_address', models.CharField(max_length=512, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessHour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(default=b'MONDAY', max_length=10, choices=[(b'MONDAY', b'Monday'), (b'TUESDAY', b'Tuesday'), (b'WEDNESDAY', b'Wednesday'), (b'THURSDAY', b'Thursday'), (b'FRIDAY', b'Friday'), (b'SATURDAY', b'Saturday'), (b'SUNDAY', b'Sunday')])),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('phone_number', models.CharField(max_length=30, null=True)),
                ('website', models.CharField(max_length=256, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_approved', models.DateTimeField(default=None, null=True)),
                ('approved', models.BooleanField(default=False)),
                ('open_street_map_id', models.IntegerField(null=True)),
                ('google_places_id', models.IntegerField(null=True)),
                ('address', models.OneToOneField(to='vp.Address')),
                ('approved_by', models.ForeignKey(related_name='approved_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('business_hours', models.ManyToManyField(to='vp.BusinessHour', null=True)),
                ('created_by', models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, choices=[(b'STORE', b'Store'), (b'BAR', b'Bar'), (b'RESTAURANT', b'Restaurant'), (b'IRISH', b'Irish'), (b'PUB', b'Pub'), (b'BEER_GARDEN', b'Beer Garden'), (b'COMEDY_CLUB', b'Comedy Club'), (b'KARAOKE_CLUB', b'Karaoke Club'), (b'DRAG', b'Drag'), (b'SPORTS', b'Sports'), (b'WINE_BAR', b'Wine Bar'), (b'DIVE_BAR,', b'Dive Bar'), (b'SALSA', b'Salsa'), (b'GAY', b'Gay'), (b'CLUB_DANCE_BAR', b'Club/Dance'), (b'HOTEL', b'Hotel'), (b'TOPLESS', b'Topless')])),
                ('parent', models.ManyToManyField(related_name='parent_rel_+', null=True, to='vp.LocationType', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, choices=[(b'LIQUOR', b'Liquor'), (b'BEER', b'Beer'), (b'CIGARETTES', b'Cigarettes'), (b'WINE', b'Wine'), (b'CIGARS', b'Cigars')])),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='location_types',
            field=models.ManyToManyField(to='vp.LocationType'),
        ),
        migrations.AddField(
            model_name='location',
            name='product_categories',
            field=models.ManyToManyField(to='vp.ProductCategory'),
        ),
    ]
