from django.conf import settings
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.annotation.mailgun import send_mail
from apps.annotation.responses import ValidationErrorResponse
from apps.annotation.serializers import AnnotationRequestDeserializer


class AnnotationRequests(APIView):

    @swagger_auto_schema(request_body=AnnotationRequestDeserializer,
                         responses={200: AnnotationRequestDeserializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = AnnotationRequestDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        data = deserializer.validated_data['attributes']

        subject = 'Prośba o przypis w tekście' if data.get('quote') else 'Prośba o przypis'
        text = '''
Użytkownik zgłosił prośbę o przypis!
URL: {}
Fragment: {}
        '''.format(data['url'], data.get('quote'))

        if not (settings.TEST or settings.DEBUG):
            send_mail(
                sender='prosba-o-przypis',
                to_addr='przypispowszechny@gmail.com',
                subject=subject,
                text=text,
            )
        return Response(deserializer.data)
