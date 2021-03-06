# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-07 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pp', '0019_annotation_add_url_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='annotation_link',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='url',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='url_id',
            field=models.CharField(blank=True, max_length=2048),
        ),
        migrations.AlterField(
            model_name='annotationrequest',
            name='url',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='annotationrequest',
            name='url_id',
            field=models.CharField(blank=True, max_length=2048),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='annotation_link',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='url',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='url_id',
            field=models.CharField(blank=True, max_length=2048),
        ),
    ]
