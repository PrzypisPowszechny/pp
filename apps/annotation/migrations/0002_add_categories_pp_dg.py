# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-09-17 23:52
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F

NORMAL = 'NORMAL'
WARNING = 'WARNING'
ALERT = 'ALERT'

ADDITIONAL_INFO = 'ADDITIONAL_INFO'
CLARIFICATION = 'CLARIFICATION'
ERROR = 'ERROR'


def init_pp_category(apps, schema):
    annotation_model = apps.get_model('annotation.Annotation')
    historical_annotation_model = apps.get_model('annotation.HistoricalAnnotation')

    annotation_model.objects.filter(priority=NORMAL).update(pp_category=ADDITIONAL_INFO)
    annotation_model.objects.filter(priority=WARNING).update(pp_category=CLARIFICATION)
    annotation_model.objects.filter(priority=ALERT).update(pp_category=ERROR)

    historical_annotation_model.objects.filter(priority=NORMAL).update(pp_category=ADDITIONAL_INFO)
    historical_annotation_model.objects.filter(priority=WARNING).update(pp_category=CLARIFICATION)
    historical_annotation_model.objects.filter(priority=ALERT).update(pp_category=ERROR)


def reverse_init_fact_category(apps, schema):
    annotation_model = apps.get_model('annotation.Annotation')
    historical_annotation_model = apps.get_model('annotation.HistoricalAnnotation')
    annotation_model.objects.update(fact_category=F('priority'))
    historical_annotation_model.objects.update(fact_category=F('priority'))


class Migration(migrations.Migration):
    dependencies = [
        ('annotation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='fact_category',
            field=models.CharField(
                choices=[('NORMAL', 'normalny'), ('WARNING', 'ostrzegawczy'), ('ALERT', 'niebezpieczny')],
                default='unset', max_length=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='fact_category',
            field=models.CharField(
                choices=[('NORMAL', 'normalny'), ('WARNING', 'ostrzegawczy'), ('ALERT', 'niebezpieczny')],
                default='unset', max_length=10),
            preserve_default=True,
        ),

        migrations.RunPython(migrations.RunPython.noop, reverse_init_fact_category),

        migrations.RemoveField(
            model_name='annotation',
            name='fact_category',
        ),
        migrations.RemoveField(
            model_name='historicalannotation',
            name='fact_category',
        ),
        migrations.AddField(
            model_name='annotation',
            name='demagog_category',
            field=models.CharField(blank=True, choices=[('TRUE', 'Prawda'), ('PTRUE', 'Prawda'), ('FALSE', 'Fałsz'),
                                                        ('PFALSE', 'Fałsz'), ('LIE', 'Manipulacja'),
                                                        ('UNKNOWN', 'Nieweryfikowalne')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='annotation',
            name='pp_category',
            field=models.CharField(
                choices=[('ADDITIONAL_INFO', 'Dodatkowa Informacja'), ('CLARIFICATION', 'Doprecyzowanie'),
                         ('ERROR', 'Sprostowanie błędu')], default='non', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalannotation',
            name='demagog_category',
            field=models.CharField(blank=True, choices=[('TRUE', 'Prawda'), ('PTRUE', 'Prawda'), ('FALSE', 'Fałsz'),
                                                        ('PFALSE', 'Fałsz'), ('LIE', 'Manipulacja'),
                                                        ('UNKNOWN', 'Nieweryfikowalne')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='historicalannotation',
            name='pp_category',
            field=models.CharField(
                choices=[('ADDITIONAL_INFO', 'Dodatkowa Informacja'), ('CLARIFICATION', 'Doprecyzowanie'),
                         ('ERROR', 'Sprostowanie błędu')], default='non', max_length=20),
            preserve_default=False,
        ),

        migrations.RunPython(init_pp_category, migrations.RunPython.noop)
    ]
