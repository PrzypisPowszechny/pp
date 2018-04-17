from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import SimpleFieldInspector, NotHandled, FieldInspector
from rest_framework import serializers

from apps.pp.models import ReferenceReport
from .models import Reference, UserReferenceFeedback


def data_wrapped(serializer):
    if isinstance(serializer, serializers.BaseSerializer):
        serializer_class = serializer.__class__
    else:
        # Initialize if class was passed instead of instance
        serializer_class = serializer
        serializer = serializer_class()
    return type('%sData' % serializer_class.__name__, (serializers.Serializer,), {'data': serializer})


def get_relationship_id(root_serializer, name):
    path = ['relationships', name, 'data', 'id']
    val = root_serializer.validated_data
    while path and val:
        key = path.pop(0)
        val = val.get(key)
    return val


def get_resource_name(model, attr=None):
    if attr not in (None, 'pk', 'id'):
        model = model._meta.get_field(attr).related_model
    return model.JSONAPIMeta.resource_name


def set_relationship(root_data, obj, attr):
    resource = get_resource_name(obj, attr)
    val = getattr(obj, attr)
    if val is None:
        data = None
    else:
        data = {
            'type': resource, 'id': val
        }
    root_data.setdefault('relationships', {})[resource[:-1]] = {'data':  data}


class IDField(serializers.IntegerField):
    def to_representation(self, value):
        value = super().to_representation(value)
        return str(value)


class IDFieldInspector(SimpleFieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if not isinstance(field, IDField):
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, **kwargs)
        return SwaggerType(type=openapi.TYPE_STRING, format='ID')


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


class ResourceIdSerializer(serializers.Serializer):
    id = IDField(required=True)


class ResourceTypeSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)


class ResourceSerializer(ResourceIdSerializer, ResourceTypeSerializer):
    pass


class ReferenceDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title')

    class Relationships(serializers.Serializer):
        class ReferenceRequest(ResourceSerializer):
            pass

        reference_request = data_wrapped(ReferenceRequest(required=False, allow_null=True))(required=False, allow_null=True)

    attributes = Attributes()
    relationships = Relationships(required=False)


class ReferenceSerializer(ResourceSerializer, ReferenceDeserializer):

    class Attributes(ReferenceDeserializer.Attributes):
        useful_count = serializers.SerializerMethodField()
        objection_count = serializers.SerializerMethodField()
        useful = serializers.SerializerMethodField('is_useful')
        objection = serializers.SerializerMethodField('is_objection')
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = ReferenceDeserializer.Attributes.Meta.model

            fields = ReferenceDeserializer.Attributes.Meta.fields + (
                'useful', 'useful_count', 'objection', 'objection_count', 'does_belong_to_user',
            )

        @property
        def request_user(self):
            return self.context['request'].user if self.context.get('request') else None

        def get_useful_count(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, useful=True)\
                                        .count()

        def get_objection_count(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, objection=True)\
                                        .count()

        def is_useful(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, useful=True)\
                                        .exists()

        def is_objection(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, objection=True)\
                                        .exists()

        def get_does_belong_to_user(self, instance):
            assert self.request_user is not None
            return self.request_user.id == instance.user_id

    class Relationships(ReferenceDeserializer.Relationships):
        class User(ResourceSerializer):
            pass

        user = data_wrapped(User)(required=True)

    attributes = Attributes()
    relationships = Relationships()


class ReferenceListSerializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        useful_count = serializers.IntegerField(default=0)
        objection_count = serializers.IntegerField(default=0)
        useful = serializers.BooleanField(default=False)
        objection = serializers.BooleanField(default=False)
        does_belong_to_user = serializers.BooleanField(default=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title',
                      'useful', 'useful_count', 'objection', 'objection_count',
                      'does_belong_to_user',
                      )
            read_only_fields = ('useful', 'useful_count', 'objection', 'objection_count',
                                'does_belong_to_user')

    class Relationships(serializers.Serializer):
        class User(ResourceSerializer):
            pass

        class ReferenceRequest(ResourceSerializer):
            pass

        user = data_wrapped(User)(required=True)
        reference_request = data_wrapped(ReferenceRequest)(required=False, allow_null=True)

    attributes = Attributes()
    relationships = Relationships()


class ReferencePatchDeserializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = Reference
            fields = ('priority', 'comment', 'reference_link', 'reference_link_title')

    attributes = Attributes()


class ReferenceReportDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = ReferenceReport
            fields = ('reason', 'comment')

    attributes = Attributes()


class ReferenceReportSerializer(ResourceSerializer, ReferenceReportDeserializer):
    class Relationships(serializers.Serializer):
        class User(ResourceSerializer):
            pass

        class Reference(ResourceSerializer):
            pass

        user = data_wrapped(User)(required=True, allow_null=True)
        reference = data_wrapped(Reference)(required=True, allow_null=True)

    relationships = Relationships()
