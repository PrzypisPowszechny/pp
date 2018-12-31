from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.annotation.tasks import notify_annotation_url_subscribers
from .models import Annotation


@receiver(post_save, sender=Annotation)
def notify_subscribers(sender, instance, **kwargs):
    notify_annotation_url_subscribers.delay(instance.id)
