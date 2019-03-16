from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.annotation import serializers
from apps.annotation.models import Annotation, AnnotationReport
from apps.api.responses import ValidationErrorResponse, NotFoundResponse, ErrorResponse


class AnnotationReportList(APIView):

    @swagger_auto_schema(request_body=serializers.AnnotationReportDeserializer,
                         responses={200: serializers.AnnotationReportSerializer})
    def post(self, request):
        deserializer = serializers.AnnotationReportDeserializer(data=request.data, context={'request': request})
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        report = AnnotationReport(**deserializer.validated_data['attributes'])
        report.user_id = request.user.pk
        report.annotation_id = deserializer.validated_data['relationships']['annotation']

        # TODO: make this validation in serializer, because: 1. if you can validate there 2. for friendly error message
        try:
            Annotation.objects.get(active=True, id=report.annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()

        try:
            report.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object.')

        return Response(serializers.AnnotationReportSerializer(
            instance={
                'id': report,
                'attributes': report,
                'relationships': {
                    'annotation': report.annotation_id,
                }
            },
            context={'request': request, 'root_resource_obj': report}
        ).data)
