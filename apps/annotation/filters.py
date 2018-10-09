import coreapi
import coreschema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend

from apps.annotation.utils import standardize_url_id


class GenericFilterBackend(DjangoFilterBackend):
    def get_filter_params(self, request):
        raise NotImplementedError

    def get_filter_schema_location(self):
        raise NotImplementedError

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(self.get_filter_params(request), queryset=queryset, request=request).qs

        return queryset

    def get_schema_fields(self, view):
        fields = super().get_schema_fields(view)
        for field in fields:
            field.location = self.get_filter_schema_location()
        return fields


class StandardizedURLFilterBackend(GenericFilterBackend):
    url_data_field = 'url'
    url_model_field = 'url_id'

    def filter_queryset(self, request, queryset, view):
        query_val = self.get_filter_params(request).get(self.url_data_field)
        if query_val:
            queryset = queryset.filter(**{
                "{field}__exact".format(field=self.url_model_field): standardize_url_id(query_val)
            })
        return queryset


class StandardizedURLBodyFilterBackend(StandardizedURLFilterBackend):
    def get_filter_params(self, request):
        return request.data

    def get_filter_schema_location(self):
        return 'body'


class StandardizedURLQueryFilterBackend(StandardizedURLFilterBackend):
    def get_filter_params(self, request):
        return request.query_params

    def get_filter_schema_location(self):
        return 'query'


class BodyFilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(request.data, queryset=queryset, request=request).qs

        return queryset
