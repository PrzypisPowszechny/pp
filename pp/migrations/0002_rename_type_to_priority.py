# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-12 20:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reference',
            old_name='reference_type',
            new_name='reference_priority',
        ),
    ]
