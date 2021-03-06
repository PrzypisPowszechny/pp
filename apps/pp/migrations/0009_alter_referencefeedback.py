# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-01 19:52
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pp', '0008_referencereport'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreferencefeedback',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userreferencefeedback',
            name='objection',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userreferencefeedback',
            name='useful',
            field=models.BooleanField(default=False),
        ),
    ]
