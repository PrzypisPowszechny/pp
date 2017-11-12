from django.db import models
from django.contrib.auth.models import User
import consts


class PPUser(User):
    pass


class Annotation(models.Model):
    user = models.ForeignKey('PPUser')
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ReferenceRequest(Annotation):
    pass


class Reference(Annotation):
    range = models.TextField(max_length=1000)
    # Json data with information aboute the annotation location

    quote = models.TextField(max_length=250)
    # The exact annotated text part

    reference_priority = models.CharField(choices=consts.annotation_priorities, max_length=100)
    comment = models.TextField(max_length=100)

    link = models.CharField(max_length=100)
    # A hyperlink

    link_title = models.CharField(max_length=100)
    # Short summary of the page referred to

    reference_request = models.ForeignKey(ReferenceRequest, null=True)
    # Null when the annotation has not been created on request



class UserReferenceFeedback(models.Model):
    user = models.ForeignKey('PPUser')
    reference = models.ForeignKey(Reference)

    useful = models.BooleanField()
    objection = models.BooleanField()

    class Meta:
        unique_together = [('user', 'reference')]


class UserReferenceRequestFeedback(models.Model):
    user = models.ForeignKey('PPUser')
    reference_request = models.ForeignKey(ReferenceRequest)

    class Meta:
        unique_together = [('user', 'reference_request')]