# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-29 23:00
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('annotation', '0007_alter_type_publisher_annotation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='annotation_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='annotation.AnnotationRequest'),
        ),
    ]
