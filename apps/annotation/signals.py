from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.annotation.tasks import notify_annotation_url_subscribers
from .models import Annotation


@receiver(post_save, sender=Annotation)
def notify_subscribers(sender, instance, raw, created, **kwargs):
    if created:
        notify_annotation_url_subscribers.apply_async(args=[instance.id])
