from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.annotation import serializers
from apps.annotation.models import Annotation, AnnotationReport
from apps.annotation.responses import ValidationErrorResponse, NotFoundResponse, ErrorResponse
from apps.annotation.views.decorators import allow_lazy_user_smart


class AnnotationReportSingle(APIView):

    @swagger_auto_schema(responses={200: serializers.AnnotationReportSerializer})
    @method_decorator(allow_lazy_user_smart)
    def get(self, request, report_id):
        try:
            report = AnnotationReport.objects.get(id=report_id, user=request.user)
        except AnnotationReport.DoesNotExist:
            return NotFoundResponse()

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


class AnnotationReportList(APIView):

    @swagger_auto_schema(request_body=serializers.AnnotationReportDeserializer,
                         responses={200: serializers.AnnotationReportSerializer})
    @method_decorator(allow_lazy_user_smart)
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


# TODO: add test
class AnnotationRelatedAnnotationReportList(APIView):

    @swagger_auto_schema(responses={200: serializers.AnnotationReportSerializer(many=True)})
    def get(self, request, annotation_id):
        try:
            Annotation.objects.get(active=True, id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()
        reports = AnnotationReport.objects.filter(annotation_id=annotation_id, user=request.user)

        return Response([
            serializers.AnnotationReportSerializer(
                instance={
                    'id': report,
                    'attributes': report,
                    'relationships': {
                        'annotation': report.annotation_id,
                    }
                },
                context={'request': request, 'root_resource_obj': report}
            ).data
            for report in reports])

