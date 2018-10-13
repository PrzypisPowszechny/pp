# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-08 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0006_reinsert_demagog_mock_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='publisher_annotation_id',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='publisher_annotation_id',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
    ]