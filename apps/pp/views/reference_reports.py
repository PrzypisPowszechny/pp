from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import Reference, ReferenceReport
from apps.pp.responses import ValidationErrorResponse, NotFoundResponse, ErrorResponse
from apps.pp.serializers import ReferenceReportSerializer, ReferenceReportDeserializer
from apps.pp.utils import get_relationship_id, DataPreSerializer, get_resource_name


# TODO: add test
class ReferenceRelatedReferenceReportList(APIView):

    @swagger_auto_schema(responses={200: ReferenceReportSerializer(many=True)})
    def get(self, request, reference_id):
        try:
            Reference.objects.get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()
        reports = ReferenceReport.objects.filter(reference_id=reference_id, user=request.user)

        data_list = []
        for report in reports:
            pre_serializer = DataPreSerializer(report, {'attributes': report})
            pre_serializer.set_relation(get_resource_name(report, related_field='reference_id'),
                                        resource_id=report.reference_id)
            pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                        resource_id=report.user_id)
            data_list.append(pre_serializer.data)
        return Response(ReferenceReportSerializer(data_list, many=True, context={'request': request}).data)


# TODO: add test
class ReferenceReportSingle(APIView):

    @swagger_auto_schema(responses={200: ReferenceReportSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, report_id):
        try:
            report = ReferenceReport.objects.get(id=report_id, user=request.user)
        except ReferenceReport.DoesNotExist:
            return NotFoundResponse()

        pre_serializer = DataPreSerializer(report, {'attributes': report})
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='reference_id'),
                                    resource_id=report.reference_id)
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                    resource_id=report.user_id)
        return Response(ReferenceReportSerializer(pre_serializer.data, context={'request': request}).data)


class ReferenceReportList(APIView):

    @swagger_auto_schema(request_body=ReferenceReportDeserializer,
                         responses={200: ReferenceReportSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = ReferenceReportDeserializer(data=request.data, context={'request': request})
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        report = ReferenceReport(**deserializer.validated_data['attributes'])
        report.user_id = request.user.pk
        report.reference_id = get_relationship_id(deserializer, 'reference')

        # TODO: make this validation in serializer, because: 1. if you can validate there 2. for friendly error message
        try:
            Reference.objects.get(active=True, id=report.reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()

        try:
            report.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object.')

        pre_serializer = DataPreSerializer(report, {'attributes': report})
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='reference_id'),
                                    resource_id=report.reference_id)
        pre_serializer.set_relation(resource_name=get_resource_name(report, related_field='user_id'),
                                    resource_id=report.user_id)
        return Response(ReferenceReportSerializer(pre_serializer.data, context={'request': request}).data)

