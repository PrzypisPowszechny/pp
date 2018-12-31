from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import SimpleFieldInspector, NotHandled, FieldInspector
from rest_framework import serializers

from .fields import IDField, ObjectField


class IDFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if not isinstance(field, IDField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, **kwargs)
        return SwaggerType(type=openapi.TYPE_STRING, format='ID')


class ObjectFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if not isinstance(field, ObjectField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, **kwargs)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            additional_properties=True,
            description='any valid object',
        )


class RootSerializerInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if (
                isinstance(obj, serializers.BaseSerializer) and
                obj.parent is None and
                method_name == 'field_to_swagger_object'
        ):
            return self.decorate_with_data(result)
        return result

    def decorate_with_data(self, result):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties=OrderedDict((
                ('data', result),
            ))
        )
