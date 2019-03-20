import logging

from django.utils.text import Truncator
from rest_framework.response import Response

from apps.annotation.mailgun import send_mail, MailSendException
from apps.annotation.serializers import AnnotationRequestSerializer

logger = logging.getLogger('pp.annotation')

mail_template = '''
Użytkownik zgłosił prośbę o przypis!
URL: {url}
Fragment: {quote}
'''


def notify_editors_about_annotation_request(annotation_request):
    # Send e-mail to Przypis Powszechny postbox
    subject = 'Prośba o przypis w tekście' if annotation_request.quote else 'Prośba o przypis'
    text = mail_template.format(url=annotation_request.url, quote=annotation_request.quote)

    try:
        send_mail(
            sender='prosba-o-przypis',
            receiver='przypispowszechny@gmail.com',
            subject=subject,
            text=text,
        )
    except MailSendException as e:
        logger.error('Annotation request (url: {url}, quote: {quote}) could not be sent by e-mail: {e}'.format(
            url=annotation_request.url,
            quote=Truncator(annotation_request.quote).chars(20),
            e=str(e))
        )
