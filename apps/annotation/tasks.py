import logging

from django.conf import settings
from django.core.signing import Signer
from django.urls import reverse

from apps.annotation.mailgun import send_mail, MailSendException
from apps.annotation.models import Annotation, AnnotationRequest
from worker import celery_app

logger = logging.getLogger('pp.annotation')


@celery_app.task
def notify_annotation_url_subscribers(annotation_id):
    annotation = Annotation.objects.get(pk=annotation_id)
    annotation_requests = AnnotationRequest.objects.filter(url_id=annotation.url_id)
    url = annotation.url

    notification_emails = []
    recipient_variables = {}
    for instance in annotation_requests:
        if instance.notification_email:
            notification_emails.append((instance.notification_email, None))
            token = Signer().sign(instance.id).split(':')[1]
            unsubscribe_reverse = reverse('site:annotation_request_unsubscribe',
                                          kwargs={'annotation_request_id': instance.id, 'token': token})
            unsubscribe_link = '{}{}'.format(settings.HOST, unsubscribe_reverse)
            recipient_variables[instance.notification_email] = {'unsubscribe_link': unsubscribe_link}
    if not notification_emails:
        return

    # TODO: format as HTML
    subject = 'Dodano przypis na stronie, na którą czytałeś'
    text = '''
            Hej,
            Ostatnio skorzystałeś z "poproś o przypis" na stronie {}.
            Właśnie ktoś dodał na niej przypis. Możliwe, że odpowiada na Twoje zgłoszenie!
            Sprawdź!
            {}
            By zrezygnować z subskrypcji, wejdź tutaj: %recipient.unsubscribe_link%
                    '''.format(url, url)

    try:
        send_mail(
            sender='dodano-przypis',
            receiver=notification_emails,
            subject=subject,
            text=text,
            recipient_variables=recipient_variables,
        )
    except MailSendException as e:
        logger.error('Annotation request notification (url: {}) could not be sent by e-mail: {}'.format(
            url,
            str(e),
        ))
