# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-19 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='objection_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reference',
            name='useful_count',
            field=models.IntegerField(default=0),
        ),
    ]
