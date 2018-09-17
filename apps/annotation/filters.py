import coreapi
import coreschema
from rest_framework.filters import BaseFilterBackend

from apps.annotation.utils import standardize_url_id


class StandardizedURLFilterBackend(BaseFilterBackend):
    url_data_field = 'url'
    url_model_field = 'url_id'

    def filter_queryset(self, request, queryset, view):
        query_val = request.query_params.get(self.url_data_field)
        if query_val:
            return queryset.filter(**{
                "{field}__exact".format(field=self.url_model_field): standardize_url_id(query_val)
            })
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.url_data_field,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='',
                    description=''
                )
            )
        ]
