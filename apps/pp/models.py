from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords

from apps.pp import consts

URL_SUPPORTED_LENGTH = 2048


class User(AbstractUser):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'users'


class UserInput(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AnnotationBase(UserInput):
    url = models.CharField(max_length=URL_SUPPORTED_LENGTH)
    # URL where the annotation has been made

    url_id = models.CharField(max_length=URL_SUPPORTED_LENGTH, blank=True)
    # Processed URL striped of some (probably) irrelevant data that might make identification harder

    range = models.TextField(max_length=1000, blank=True)
    # Json data with information about the annotation location

    quote = models.TextField(max_length=250)
    # The exact annotated text part

    quote_context = models.TextField(max_length=250, blank=True)
    # The annotated text with its surrounding

    active = models.BooleanField(blank=True, default=True)

    # We never actually delete models -- we only mark them as not active

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from apps.pp.utils import standardize_url_id
        self.url_id = standardize_url_id(self.url)
        super().save(*args, **kwargs)


class AnnotationRequest(AnnotationBase):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'annotation_requests'


class Annotation(AnnotationBase):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'annotations'

    publisher = models.CharField(choices=consts.publishers, max_length=10, default=consts.PP_PUBLISHER)

    priority = models.CharField(choices=consts.annotation_priorities, max_length=10)
    comment = models.TextField(max_length=1000)

    annotation_link = models.CharField(max_length=URL_SUPPORTED_LENGTH)
    # A hyperlink

    annotation_link_title = models.CharField(max_length=110)
    # Short summary of the page referred to

    annotation_request = models.ForeignKey('AnnotationRequest', null=True)
    # Null when the annotation has not been created on request

    history = HistoricalRecords()

    # django-simple-history used here

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def count_upvote(self):
        self.upvote_count = AnnotationUpvote.objects.filter(annotation=self).count()
        return self.upvote_count


class AnnotationReport(UserInput):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'annotation_reports'

    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='annotation_reports')
    reason = models.CharField(choices=consts.annotation_report_reasons, max_length=100)
    comment = models.TextField(max_length=100)


class AnnotationUpvote(UserInput):
    class Meta:
        app_label = 'pp'
        unique_together = [('user', 'annotation')]

    class JSONAPIMeta:
        resource_name = 'annotation_upvotes'

    annotation = models.ForeignKey(Annotation, related_name='feedbacks')


class AnnotationRequestFeedback(models.Model):
    class Meta:
        app_label = 'pp'
        unique_together = [('user', 'annotation_request')]

    class JSONAPIMeta:
        resource_name = 'annotation_request_feedbacks'

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    annotation_request = models.ForeignKey(AnnotationRequest)
