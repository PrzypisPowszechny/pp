import logging
from distutils.util import strtobool

import rest_framework_json_api.parsers
import rest_framework_json_api.renderers

import django_filters
from django.apps import apps
from django.forms import NullBooleanSelect, BooleanField, CharField
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation.filters import ConflictingFilterValueError
from apps.annotation.mails import notify_editors_about_annotation_request
from apps.annotation.models import AnnotationRequest
from apps.annotation.serializers import AnnotationRequestDeserializer, AnnotationRequestSerializer
from apps.api.permissions import OnlyOwnerCanChange
from apps.api.responses import ValidationErrorResponse, NotFoundResponse, PermissionDenied


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


class AnnotationRequestViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):

    serializer_class = AnnotationRequestSerializer
    queryset = AnnotationRequest.objects.filter(active=True).prefetch_related('annotation_set')
    renderer_classes = [rest_framework_json_api.renderers.JSONRenderer]
    parser_classes = [rest_framework_json_api.parsers.JSONParser]
    permission_classes = [OnlyOwnerCanChange]
    owner_field = 'user'

    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ('create_date',)
    ordering = "-create_date"
    filterset_class = AnnotationRequestFilterSet

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        notify_editors_about_annotation_request(instance)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()

