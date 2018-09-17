# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-26 21:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0011_rename_feedback_to_upvote'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserReferenceRequestFeedback',
            new_name='UserAnnotationRequestFeedback',
        ),
        migrations.RenameModel(
            old_name='ReferenceRequest',
            new_name='AnnotationRequest',
        ),
        migrations.AlterUniqueTogether(
            name='userannotationrequestfeedback',
            unique_together=set([]),
        ),
        migrations.RenameField(
            model_name='userannotationrequestfeedback',
            old_name='reference_request',
            new_name='annotation_request',
        ),
        migrations.RenameField(
            model_name='historicalreference',
            old_name='reference_request',
            new_name='annotation_request',
        ),
        migrations.RenameField(
            model_name='reference',
            old_name='reference_request',
            new_name='annotation_request',
        ),
        migrations.AlterUniqueTogether(
            name='userannotationrequestfeedback',
            unique_together=set([('user', 'annotation_request')]),
        ),
    ]
