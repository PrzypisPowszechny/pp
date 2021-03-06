# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-03 14:49
from __future__ import unicode_literals

import json

from django.db import migrations


def string_to_json_string(apps, schema):
    annotation_class = apps.get_model('pp.Annotation')
    for annotation in annotation_class.objects.all():
        try:
            json.loads(annotation.range)
        except ValueError:
            annotation.range = '"%s"' % annotation.range
            annotation.save()


def json_string_to__string(apps, schema):
    annotation_class = apps.get_model('pp.Annotation')
    for annotation in annotation_class.objects.all():
        if len(annotation.range) >= 2 and annotation.range[0] == '"' and annotation.range[-1] == '"':
            annotation.range = annotation.range[1:-1]
            annotation.save()


class Migration(migrations.Migration):
    dependencies = [
        ('pp', '0017_rename_all_annotation_related_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='annotation',
            old_name='ranges',
            new_name='range',
        ),
        migrations.RenameField(
            model_name='annotationrequest',
            old_name='ranges',
            new_name='range',
        ),
        migrations.RenameField(
            model_name='historicalannotation',
            old_name='ranges',
            new_name='range',
        ),
        migrations.RunPython(string_to_json_string, json_string_to__string)
    ]
