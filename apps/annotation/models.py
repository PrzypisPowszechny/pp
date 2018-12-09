
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.annotation import consts

URL_SUPPORTED_LENGTH = 2048


class UserInput(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class AnnotationBase(UserInput):
    url = models.CharField(max_length=URL_SUPPORTED_LENGTH)
    # URL where the annotation has been made

    url_id = models.CharField(max_length=URL_SUPPORTED_LENGTH, blank=True)
    # Processed URL striped of some (probably) irrelevant data that might make identification harder

    active = models.BooleanField(blank=True, default=True)

    # We never actually delete models -- we only mark them as not active

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from apps.annotation.utils import standardize_url_id
        self.url_id = standardize_url_id(self.url)
        super().save(*args, **kwargs)


class LocatedAnnotationBase(AnnotationBase):
    range = models.TextField(max_length=1000, blank=True)
    # Json data with information about the annotation location

    quote = models.TextField(max_length=250)
    # The exact annotated text part

    quote_context = models.TextField(max_length=250, blank=True)
    # The annotated text with its surrounding

    class Meta:
        abstract = True


class AnnotationRequest(AnnotationBase):

    class JSONAPIMeta:
        resource_name = 'annotation_requests'

    quote = models.TextField(max_length=250, blank=True)
    # The exact annotated text part

    comment = models.TextField(max_length=250, blank=True)

    notification_email = models.EmailField(max_length=250, blank=True)


class Annotation(LocatedAnnotationBase):

    class JSONAPIMeta:
        resource_name = 'annotations'

    PP_PUBLISHER = 'PP'
    DEMAGOG_PUBLISHER = 'DEMAGOG'

    PUBLISHERS = (
        (PP_PUBLISHER, 'Przypis Powszechny'),
        (DEMAGOG_PUBLISHER, 'Demagog'),
    )

    ADDITIONAL_INFO = 'ADDITIONAL_INFO'
    CLARIFICATION = 'CLARIFICATION'
    ERROR = 'ERROR'

    PP_CATERORIES = (
        (ADDITIONAL_INFO, 'Dodatkowa Informacja'),
        (CLARIFICATION, 'Doprecyzowanie'),
        (ERROR, 'Sprostowanie błędu'),
    )

    TRUE = 'TRUE'
    PTRUE = 'PTRUE'
    FALSE = 'FALSE'
    PFALSE = 'PFALSE'
    LIE = 'LIE'
    UNKOWN = 'UNKNOWN'

    DEMAGOG_CATEGORIES = (
        (TRUE, 'Prawda'),
        (PTRUE, 'Prawda'),
        (FALSE, 'Fałsz'),
        (PFALSE, 'Fałsz'),
        (LIE, 'Manipulacja'),
        (UNKOWN, 'Nieweryfikowalne'),
    )

    UNVERIFIED = 'UNVERIFIED'
    CONFIRMED = 'CONFIRMED'
    UNLOCATED = 'UNLOCATED'
    UNLOCATABLE = 'UNLOCATABLE'
    ARTICLE_DOES_NOT_EXIST = 'ARTICLE_DOES_NOT_EXIST'
    PAGE_404 = 'PAGE_404'
    OTHER_FATAL = 'OTHER_FATAL'

    CHECK_STATUSES = (
        (UNVERIFIED, 'niesprawdzony (wyświetlany)'),
        (CONFIRMED, 'potwierdzony'),
        (UNLOCATED, 'nie lokalizuje się (a mógłby)'),
        (UNLOCATABLE, 'nielokalizowalny (video/audio/...)'),
        (ARTICLE_DOES_NOT_EXIST, 'artykuł nie istnieje'),
        (PAGE_404, 'strona nie istnieje'),
        (OTHER_FATAL, 'inne -- nie można wyświetlić'),
    )

    publisher = models.CharField(choices=PUBLISHERS, max_length=10, default=PP_PUBLISHER)

    publisher_annotation_id = models.CharField(db_index=True, blank=True, null=True, max_length=64)

    pp_category = models.CharField(choices=PP_CATERORIES, max_length=20)
    # Category for PP publisher (and other publishers' categories mapped to pp)

    demagog_category = models.CharField(choices=DEMAGOG_CATEGORIES, max_length=20, null=True, blank=True)
    # Category for Demagog publisher

    comment = models.TextField(max_length=1000)

    annotation_link = models.CharField(max_length=URL_SUPPORTED_LENGTH)
    # A hyperlink

    check_status = models.CharField(choices=CHECK_STATUSES, max_length=30, null=True, default=UNVERIFIED)

    annotation_link_title = models.CharField(max_length=110)
    # Short summary of the page referred to

    annotation_request = models.ForeignKey('AnnotationRequest', on_delete=models.CASCADE, null=True, blank=True)
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

    class JSONAPIMeta:
        resource_name = 'annotation_reports'

    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='annotation_reports')
    reason = models.CharField(choices=consts.annotation_report_reasons, max_length=100)
    comment = models.TextField(max_length=1000, blank=True)


class AnnotationUpvote(UserInput):
    class Meta:
        unique_together = [('user', 'annotation')]

    class JSONAPIMeta:
        resource_name = 'annotation_upvotes'

    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='feedbacks')


class AnnotationRequestFeedback(models.Model):
    class Meta:
        unique_together = [('user', 'annotation_request')]

    class JSONAPIMeta:
        resource_name = 'annotation_request_feedbacks'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    annotation_request = models.ForeignKey(AnnotationRequest, on_delete=models.CASCADE)
