
import inflection
from django.db import models
from drf_yasg import openapi
from drf_yasg.inspectors import SimpleFieldInspector, NotHandled

from apps.pp.models import ReferenceReport
from .models import Reference, UserReferenceFeedback
from rest_framework import serializers


def data_wrapped(serializer):
    if isinstance(serializer, serializers.BaseSerializer):
        serializer_class = serializer.__class__
    else:
        # Initialize if class was passed instead of instance
        serializer_class = serializer
        serializer = serializer_class()
    return type('%sData' % serializer_class.__name__, (serializers.Serializer,), {'data': serializer})


def get_relationship_id(root_serializer, name):
    return root_serializer.validated_data.get('relationships', {}).get(name, {}).get('data', {}).get('id')


def set_relationship(root_data, obj_or_id, cls=None):
    if obj_or_id is None:
        if cls is None:
            raise ValueError("cls param must be provided when obj_or_id is None")
        data = None
    else:
        if isinstance(obj_or_id, int):
            pk = obj_or_id
        elif isinstance(obj_or_id, models.Model):
            pk = obj_or_id.pk
        else:
            raise ValueError('obj_or_id should be int or Model, got %s' % obj_or_id.__class__.__name__)
        cls = cls if isinstance(obj_or_id, int) else obj_or_id.__class__
        data = {
            'type': cls.JSONAPIMeta.resource_name, 'id': pk
        }
    root_data.setdefault('relationships', {})[inflection.underscore(cls.__name__)] = {'data':  data}


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


class ResourceIdSerializer(serializers.Serializer):
    id = IDField(required=True)


class ResourceTypeSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)


class ResourceSerializer(ResourceIdSerializer, ResourceTypeSerializer):
    pass


class ReferenceQuerySerializer(ResourceTypeSerializer):
    class QueryAttributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title')

    class RelationshipsQuery(serializers.Serializer):
        class ReferenceRequest(ResourceSerializer):
            pass

        reference_request = data_wrapped(ReferenceRequest)(required=False, allow_null=True)

    attributes = QueryAttributes()
    relationships = RelationshipsQuery(required=False)


class ReferenceSerializer(ResourceSerializer, ReferenceQuerySerializer):

    class Attributes(ReferenceQuerySerializer.QueryAttributes):
        useful_count = serializers.SerializerMethodField()
        objection_count = serializers.SerializerMethodField()
        useful = serializers.SerializerMethodField('is_useful')
        objection = serializers.SerializerMethodField('is_objection')
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = ReferenceQuerySerializer.QueryAttributes.Meta.model

            fields = ReferenceQuerySerializer.QueryAttributes.Meta.fields + (
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

    class Relationships(ReferenceQuerySerializer.RelationshipsQuery):
        class User(ResourceSerializer):
            pass

        user = data_wrapped(User)(required=True)

    attributes = Attributes()
    relationships = Relationships()


class ReferenceListGETSerializer(ResourceSerializer):
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


class ReferencePATCHQuerySerializer(ResourceSerializer):
    class PATCHQueryAttributes(serializers.ModelSerializer):
        class Meta:
            model = Reference
            fields = ('priority', 'comment', 'reference_link', 'reference_link_title')

    attributes = PATCHQueryAttributes()


class ReferenceReportQuerySerializer(ResourceTypeSerializer):
    class ReferenceReportQueryAttributes(serializers.ModelSerializer):
        class Meta:
            model = ReferenceReport
            fields = ('reason', 'comment')

    attributes = ReferenceReportQueryAttributes()


class ReferenceReportSerializer(ResourceSerializer, ReferenceReportQuerySerializer):
    class ReferenceReportAttributes(ReferenceReportQuerySerializer.ReferenceReportQueryAttributes):
        pass

    class ReferenceReportRelationships(serializers.Serializer):
        class User(ResourceSerializer):
            pass

        class Reference(ResourceSerializer):
            pass

        user = data_wrapped(User)(required=True, allow_null=True)
        reference = data_wrapped(Reference)(required=True, allow_null=True)

    relationships = ReferenceReportRelationships()
    attributes = ReferenceReportAttributes()
