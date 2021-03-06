# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-26 22:14
from __future__ import unicode_literals

from django.db import connection
from django.db import migrations


class Migration(migrations.Migration):
    atomic = connection.vendor is not 'sqlite'

    dependencies = [
        ('pp', '0015_rename_userannotationrequestfeedback_to_annotationrequestfeedback'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Reference',
            new_name='Annotation',
        ),
        migrations.RenameModel(
            old_name='HistoricalReference',
            new_name='HistoricalAnnotation',
        ),
        migrations.AlterModelOptions(
            name='historicalannotation',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'),
                     'verbose_name': 'historical annotation'},
        ),
    ]
