import logging
from distutils.util import strtobool

import django_filters
from django.apps import apps
from django.forms import NullBooleanSelect, BooleanField, CharField
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation.filters import ConflictingFilterValueError
from apps.annotation.mails import notify_editors_about_annotation_request
from apps.annotation.models import AnnotationRequest
from apps.annotation.serializers import AnnotationRequestDeserializer, AnnotationRequestSerializer
from apps.api.responses import ValidationErrorResponse


class NullBooleanField(CharField):
    def to_python(self, value):
        if value is None:
            return None
        try:
            return bool(strtobool(value))
        except ValueError:
            return None

    def validate(self, value):
        pass


class BooleanFilter(django_filters.Filter):
    field_class = NullBooleanField


class RequestUserBooleanFilter(django_filters.Filter):
    field_class = NullBooleanField

    def get_method_based_on_value(self, qs, value):
        return qs.filter if value else qs.exclude

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        lookup = '%s__%s' % (self.field_name, self.lookup_expr)
        qs = self.get_method_based_on_value(qs, value)(**{lookup: self.parent.request.user})
        return qs


class AnnotationRequestFilterSet(django_filters.FilterSet):
    answered = BooleanFilter(field_name='annotation', lookup_expr='isnull', exclude=True)
    belongs_to_me = RequestUserBooleanFilter(field_name='user')

    class Meta:
        model = apps.get_model('annotation.AnnotationRequest')
        fields = []


class AnnotationRequests(GenericAPIView):
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ('create_date',)
    ordering = "-create_date"
    filterset_class = AnnotationRequestFilterSet

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

        notify_editors_about_annotation_request(annotation_request)

        return Response(AnnotationRequestSerializer(
            instance={
                'id': annotation_request,
                'attributes': annotation_request,
                'relationships': {
                    'annotations': ()
                }
            },
            context={'request': request, 'root_resource_obj': annotation_request}
        ).data)

    def get_queryset(self):
        return AnnotationRequest.objects.filter(active=True).prefetch_related('annotation_set')

    @swagger_auto_schema(responses={200: AnnotationRequestSerializer(many=True)})
    def get(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ConflictingFilterValueError as e:
            return ValidationErrorResponse(e.errors)

        queryset = self.paginator.paginate_queryset(queryset, request)

        return self.get_paginated_response([
            AnnotationRequestSerializer(instance={
                'id': annotation_request,
                'attributes': annotation_request,
                'relationships': {
                    'annotations': list(annotation_request.annotation_set.all())
                }
            }, context={'request': request, 'root_resource_obj': annotation_request}).data
            for annotation_request in queryset])
