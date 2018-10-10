# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-26 21:58
from __future__ import unicode_literals

from django.db import migrations
from django.db import connection


class Migration(migrations.Migration):
    atomic = connection.vendor is not 'sqlite'

    dependencies = [
        ('pp', '0013_rename_referencereport_to_annotationreport'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReferenceUpvote',
            new_name='AnnotationUpvote',
        ),
    ]
