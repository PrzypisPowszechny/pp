import coreapi
import coreschema
from drf_yasg import openapi
from rest_framework.filters import BaseFilterBackend

from apps.annotation.utils import standardize_url_id


class ConflictingFilterValueError(Exception):
    def __init__(self, errors, *args, **kwargs):
        self.errors = errors
        super(*args, **kwargs)


class StandardizedURLFilterBackend(BaseFilterBackend):

    secret_url_header = 'PP-SITE-URL' # the actual HTTP key
    secret_url_meta_key = 'HTTP_PP_SITE_URL' # the key after Django middleware processing

    url_data_query_param = 'url'

    url_model_field = 'url_id'

    def filter_queryset(self, request, queryset, view):
        header_value = request.META.get(self.secret_url_meta_key)
        param_value = request.query_params.get(self.url_data_query_param)
        if header_value and param_value and header_value != param_value:
            raise ConflictingFilterValueError({'url': 'Different URLs specified via header and via params; '
                                              'please use only one of these'})

        filter_value = header_value or param_value
        if filter_value:
            return queryset.filter(**{
                "{field}__exact".format(field=self.url_model_field): standardize_url_id(filter_value)
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
