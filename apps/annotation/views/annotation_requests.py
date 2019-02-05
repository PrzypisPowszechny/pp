import logging

from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.annotation.mailgun import send_mail, MailSendException
from apps.annotation.models import AnnotationRequest
from apps.annotation.responses import ValidationErrorResponse
from apps.annotation.serializers import AnnotationRequestDeserializer, AnnotationRequestSerializer


logger = logging.getLogger('pp.annotation')


class AnnotationRequests(GenericAPIView):
    resource_name = 'annotation_requests'

    @swagger_auto_schema(request_body=AnnotationRequestDeserializer,
                         responses={200: AnnotationRequestSerializer})
    def post(self, request):
        deserializer = AnnotationRequestDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        data = deserializer.validated_data['attributes']

        annotation_request = AnnotationRequest(**data)
        annotation_request.user_id = request.user.pk
        annotation_request.save()

        # Send e-mail to Przypis Powszechny postbox
        subject = 'Prośba o przypis w tekście' if data.get('quote') else 'Prośba o przypis'
        text = '''
Użytkownik zgłosił prośbę o przypis!
URL: {}
Fragment: {}
        '''.format(data['url'], data.get('quote'))

        try:
            send_mail(
                sender='prosba-o-przypis',
                receiver='przypispowszechny@gmail.com',
                subject=subject,
                text=text,
            )
        except MailSendException as e:
            logger.error('Annotation request (url: {}, quote: {}) could not be sent by e-mail: {}'.format(
                data['url'],
                Truncator(data.get('quote', '')).chars(20),
                str(e))
            )

        return Response(AnnotationRequestSerializer(
            instance={
                'id': annotation_request,
                'attributes': annotation_request
            }).data)
