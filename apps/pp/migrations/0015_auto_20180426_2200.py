# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-26 22:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pp', '0014_auto_20180426_2158'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserAnnotationRequestFeedback',
            new_name='AnnotationRequestFeedback',
        ),
    ]
