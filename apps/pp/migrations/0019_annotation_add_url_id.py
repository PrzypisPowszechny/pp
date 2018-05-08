# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-08 14:26
from __future__ import unicode_literals

from urllib.parse import urlsplit, urlencode, parse_qsl

from django.db import migrations
from django.db import models

OMITTED_QUERY_VARS = (
    'utm_campaign',
    'utm_medium',
    'utm_term',
    'utm_name',
    'utm_source',
)


def standardize_url_index(data):
    """
    Format url in the way that:
      - ignores protocol
      - ignores fragment(anchor)
      - ignores some blacklisted query vars like utm etc
      - set '/' as a path if none given
      - removes '?' if no query string
    """
    url_parsed = urlsplit(data)
    query_tuples = parse_qsl(url_parsed.query)
    new_query_tuples = []
    for var_name, val in query_tuples:
        if var_name not in OMITTED_QUERY_VARS:
            new_query_tuples.append((var_name, val))
    return '{netloc}{path}{query}'.format(
        netloc=url_parsed.netloc,
        path=url_parsed.path if url_parsed.path else '/',
        query='?' + urlencode(new_query_tuples) if new_query_tuples else ''
    )


def migrate_one_class(model_class):
    for instance in model_class.objects.all():
        instance.url_id = standardize_url_index(instance.url)
        instance.save()


def populate_url_id(apps, schema):
    migrate_one_class(apps.get_model('pp.Annotation'))
    migrate_one_class(apps.get_model('pp.AnnotationRequest'))
    migrate_one_class(apps.get_model('pp.HistoricalAnnotation'))


class Migration(migrations.Migration):
    dependencies = [
        ('pp', '0018_rename_ranges_to_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='url_id',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='annotationrequest',
            name='url_id',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='historicalannotation',
            name='url_id',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.RunPython(populate_url_id, lambda apps, schema: None),

        migrations.AlterField(
            model_name='annotation',
            name='url_id',
            field=models.CharField(blank=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='annotationrequest',
            name='url_id',
            field=models.CharField(blank=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='url_id',
            field=models.CharField(blank=False, max_length=200),
        ),
    ]
