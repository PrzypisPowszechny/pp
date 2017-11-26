from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.pp import consts


class User(AbstractUser):
    class JSONAPIMeta:
        resource_name = 'users'


class Annotation(models.Model):
    user = models.ForeignKey('User')
    create_date = models.DateTimeField(auto_now_add=True)

    url = models.CharField(max_length=200)
    # URL where the annotation has been made

    ranges = models.TextField(max_length=1000)
    # Json data with information aboute the annotation location

    quote = models.TextField(max_length=250)

    # The exact annotated text part

    class Meta:
        abstract = True


class ReferenceRequest(Annotation):
    class JSONAPIMeta:
        resource_name = 'reference_requests'


class Reference(Annotation):
    priority = models.CharField(choices=consts.annotation_priorities, max_length=100)
    comment = models.TextField(max_length=100)

    link = models.CharField(max_length=100)
    # A hyperlink

    link_title = models.CharField(max_length=100)
    # Short summary of the page referred to

    reference_request = models.ForeignKey(ReferenceRequest, null=True)
    # Null when the annotation has not been created on request

    def count_useful_and_objection(self):
        self.useful_count = UserReferenceFeedback.objects.filter(reference=self).filter(useful=True).count()
        self.objection_count = UserReferenceFeedback.objects.filter(reference=self).filter(objection=True).count()
        return (self.useful_count, self.objection_count)

    class JSONAPIMeta:
        resource_name = 'references'


class UserReferenceFeedback(models.Model):
    user = models.ForeignKey('User')
    reference = models.ForeignKey(Reference, related_name='feedbacks')

    useful = models.BooleanField()
    objection = models.BooleanField()

    class Meta:
        unique_together = [('user', 'reference')]

    class JSONAPIMeta:
        resource_name = 'user_references'


class UserReferenceRequestFeedback(models.Model):
    user = models.ForeignKey('User')
    reference_request = models.ForeignKey(ReferenceRequest)

    class Meta:
        unique_together = [('user', 'reference_request')]

    class JSONAPIMeta:
        resource_name = 'user_reference_feedbacks'
