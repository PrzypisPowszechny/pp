from drf_yasg import inspectors
from drf_yasg import openapi

from apps.api.fields import ObjectField


class ObjectFieldInspector(inspectors.SimpleFieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if not isinstance(field, ObjectField):
            return inspectors.NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, **kwargs)
        swagger_object = SwaggerType(
            type=openapi.TYPE_OBJECT,
            additional_properties=True,
            description='any valid object',
        )
        if field.read_only:
            swagger_object.read_only = True
        return swagger_object

