# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-09 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0008_alter_annotation_request_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='check_status',
            field=models.CharField(choices=[('UNVERIFIED', 'niesprawdzony (wyświetlany)'), ('CONFIRMED', 'potwierdzony'), ('UNLOCATED', 'nie lokalizuje się (a mógłby)'), ('UNLOCATABLE', 'nielokalizowalny (video/audio/...)'), ('ARTICLE_DOES_NOT_EXIST', 'artykuł nie istnieje'), ('PAGE_404', 'strona nie istnieje'), ('OTHER_FATAL', 'inne -- nie można wyświetlić')], default='UNVERIFIED', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='historicalannotation',
            name='check_status',
            field=models.CharField(choices=[('UNVERIFIED', 'niesprawdzony (wyświetlany)'), ('CONFIRMED', 'potwierdzony'), ('UNLOCATED', 'nie lokalizuje się (a mógłby)'), ('UNLOCATABLE', 'nielokalizowalny (video/audio/...)'), ('ARTICLE_DOES_NOT_EXIST', 'artykuł nie istnieje'), ('PAGE_404', 'strona nie istnieje'), ('OTHER_FATAL', 'inne -- nie można wyświetlić')], default='UNVERIFIED', max_length=30, null=True),
        ),
    ]