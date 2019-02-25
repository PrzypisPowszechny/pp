# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-25 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pp', '0021_annotation_texts_lengths'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationreport',
            name='comment',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='annotationreport',
            name='reason',
            field=models.CharField(
                choices=[('BIASED', 'nieobiektywny'), ('UNRELIABLE', 'nierzetelne źródło'), ('USELESS', 'niepotrzebny'),
                         ('SPAM', 'spam'), ('OTHER', 'inne'), ('SUGGESTED_CORRECTION', 'sugerowana poprawka')],
                max_length=100),
        ),
    ]
