from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import SimpleFieldInspector, NotHandled, FieldInspector
from rest_framework import serializers

from .fields import IDField, ObjectField, RelationField, ResourceField, ConstField


class IDFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if not isinstance(field, IDField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, **kwargs)
        return SwaggerType(type=openapi.TYPE_STRING, format='ID')


class ConstFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if not isinstance(field, ConstField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        return SwaggerType(type=openapi.TYPE_STRING, pattern=field.const_value)


class ResourceFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if not isinstance(field, ResourceField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        type_schema = self.probe_field_inspectors(field.type_subfield, ChildSwaggerType, use_references)
        id_schema = self.probe_field_inspectors(field.id_subfield, ChildSwaggerType, use_references)

        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': type_schema,
                'id': id_schema,
            },
        )


class RelationFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if not isinstance(field, RelationField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        child_schema = self.probe_field_inspectors(field.child, ChildSwaggerType, use_references)
        link_child_schema = self.probe_field_inspectors(field.link_child, ChildSwaggerType, use_references)
        link_child_schema.read_only = field.link_child.read_only

        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': child_schema,
                'links': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'related': link_child_schema
                    }
                )
            },
        )


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
