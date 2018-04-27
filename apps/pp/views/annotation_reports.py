from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import Annotation, AnnotationReport
from apps.pp.responses import ValidationErrorResponse, NotFoundResponse, ErrorResponse
from apps.pp.serializers import AnnotationReportSerializer, AnnotationReportDeserializer
from apps.pp.utils import get_relationship_id, DataPreSerializer, get_resource_name


# TODO: add test
class AnnotationRelatedAnnotationReportList(APIView):

    @swagger_auto_schema(responses={200: AnnotationReportSerializer(many=True)})
    def get(self, request, annotation_id):
        try:
            Annotation.objects.get(active=True, id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()
        reports = AnnotationReport.objects.filter(annotation_id=annotation_id, user=request.user)

        data_list = []
        for report in reports:
            pre_serializer = DataPreSerializer(report, {'attributes': report})
            pre_serializer.set_relation(get_resource_name(report, related_field='annotation_id'),
                                        resource_id=report.annotation_id)
            pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                        resource_id=report.user_id)
            data_list.append(pre_serializer.data)
        return Response(AnnotationReportSerializer(data_list, many=True, context={'request': request}).data)


# TODO: add test
class AnnotationReportSingle(APIView):

    @swagger_auto_schema(responses={200: AnnotationReportSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, report_id):
        try:
            report = AnnotationReport.objects.get(id=report_id, user=request.user)
        except AnnotationReport.DoesNotExist:
            return NotFoundResponse()

        pre_serializer = DataPreSerializer(report, {'attributes': report})
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='annotation_id'),
                                    resource_id=report.annotation_id)
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                    resource_id=report.user_id)
        return Response(AnnotationReportSerializer(pre_serializer.data, context={'request': request}).data)


class AnnotationReportList(APIView):

    @swagger_auto_schema(request_body=AnnotationReportDeserializer,
                         responses={200: AnnotationReportSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = AnnotationReportDeserializer(data=request.data, context={'request': request})
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        report = AnnotationReport(**deserializer.validated_data['attributes'])
        report.user_id = request.user.pk
        report.annotation_id = get_relationship_id(deserializer, 'annotation')

        # TODO: make this validation in serializer, because: 1. if you can validate there 2. for friendly error message
        try:
            Annotation.objects.get(active=True, id=report.annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()

        try:
            report.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object.')

        pre_serializer = DataPreSerializer(report, {'attributes': report})
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='annotation_id'),
                                    resource_id=report.annotation_id)
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                    resource_id=report.user_id)
        return Response(AnnotationReportSerializer(pre_serializer.data, context={'request': request}).data)

