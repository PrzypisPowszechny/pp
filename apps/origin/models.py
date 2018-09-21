from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.annotation import consts


class AnnotationOrigin(models.Model):

    create_date = models.DateTimeField(auto_now_add=True)

    annotation = models.ForeignKey('annotation.Annotation')

    publisher = models.CharField(choices=consts.publishers, max_length=10, db_index=True)

    external_id = models.CharField(max_length=255, db_index=True)

    original_data = models.TextField(max_length=10000)
    # ALL original data stored as JSON

    history = HistoricalRecords()
