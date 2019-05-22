from distutils.util import strtobool

import coreapi
import coreschema
import django_filters
from django.forms import CharField
from django_filters.constants import EMPTY_VALUES
from drf_yasg import openapi
from rest_framework.filters import BaseFilterBackend

from apps.annotation.utils import standardize_url_id


class ConflictingFilterValueError(Exception):
    def __init__(self, errors, *args, **kwargs):
        self.errors = errors
        super(*args, **kwargs)


class StandardizedURLFilterBackend(BaseFilterBackend):
    secret_url_header = 'PP-SITE-URL'  # the actual HTTP key
    secret_url_meta_key = 'HTTP_PP_SITE_URL'  # the key after Django middleware processing

    url_data_query_param = 'url'

    def filter_queryset(self, request, queryset, view):
        assert hasattr(view, 'url_filter_model_field'), \
            f"{self.__class__.__name__} filter requires view to define url_filter_model_field attr"

        header_value = request.META.get(self.secret_url_meta_key)
        param_value = request.query_params.get(self.url_data_query_param)
        if header_value and param_value and header_value != param_value:
            raise ConflictingFilterValueError({'url': 'Different URLs specified via header and via params; '
                                                      'please use only one of these'})

        filter_value = header_value or param_value
        if filter_value:
            return queryset.filter(**{
                "{field}__exact".format(field=view.url_filter_model_field): standardize_url_id(filter_value)
            })
        return queryset

    # This non-standard header filter requires header param definiton to be injected manually into auto_swagger_schema;
    # It is provided by this method
    @classmethod
    def get_manual_parameters(cls):
        return [
            openapi.Parameter(
                name=cls.secret_url_header,
                in_=openapi.IN_HEADER,
                description='A header field for secretly passing URL (since browsing history is sensitive data)',
                type=openapi.TYPE_STRING
            )
        ]

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.url_data_query_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='',
                    description=''
                )
            )
        ]


class ListORFilter(django_filters.Filter):
    # A filter where multiple comma-separated values can be provided: ?some_param=small,big
    # Based on https://github.com/carltongibson/django-filter/issues/137#issuecomment-77697870

    def __init__(self, *args, **kwargs):
        super().__init__(lookup_expr='in', *args, **kwargs)

    def filter(self, qs, value):
        value_list = None
        if value:
            value_list = value.split(',')
        return super(ListORFilter, self).filter(qs, value_list)


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

