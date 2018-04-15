import inflection
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import format_keys

from apps.pp.models import ReferenceReport
from .models import Reference, UserReferenceFeedback, User
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty


def data_wrapped(serializer_class):
    return type('%sData' % serializer_class.__name__, (serializers.Serializer,), {'data': serializer_class()})


def get_relationship_id(root_serializer, name):
    return root_serializer.data.get('relationships', {}).get(name, {}).get('data', {}).get('id')


def set_relationship(root_data, obj_or_id, cls=None):
    if obj_or_id is None:
        if cls is None:
            raise ValueError("cls param must be provided when obj_or_id is None")
        data = None
    else:
        pk = obj_or_id if isinstance(obj_or_id, int) else obj_or_id.pk
        cls = cls if isinstance(obj_or_id, int) else obj_or_id.__class__
        data = {
            'type': cls.JSONAPIMeta.resource_name, 'id': pk
        }
    root_data.setdefault('relationships', {})[inflection.underscore(cls.__name__)] = {'data':  data}


class ReferenceQuerySerializer(serializers.Serializer):
    class QueryAttributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title')

    class RelationshipsQuery(serializers.Serializer):
        class ReferenceRequest(serializers.Serializer):
            type = serializers.CharField()
            id = serializers.IntegerField()

        reference_request = data_wrapped(ReferenceRequest)(required=False, allow_null=True)

    type = serializers.CharField(required=True)
    attributes = QueryAttributes()
    relationships = RelationshipsQuery(required=False)


class ReferenceSerializer(ReferenceQuerySerializer):
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

        def __init__(self, instance=None, data=empty, *args, **kwargs):
            super().__init__(instance, data, **kwargs)
            self.user = self.context['request'].user if self.context.get('request') else None

        def get_useful_count(self, instance):
            assert self.user is not None
            return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).count()

        def get_objection_count(self, instance):
            assert self.user is not None
            return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).count()

        def is_useful(self, instance):
            assert self.user is not None
            return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).exists()

        def is_objection(self, instance):
            assert self.user is not None
            return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).exists()

        def get_does_belong_to_user(self, instance):
            assert self.user is not None
            return self.user.id == instance.user_id

    class Relationships(ReferenceQuerySerializer.RelationshipsQuery):
        class User(serializers.Serializer):
            type = serializers.CharField(),
            id = serializers.IntegerField()
        user = data_wrapped(User)(required=True)

    id = serializers.IntegerField(required=True)
    attributes = Attributes()
    relationships = Relationships()


class ReferenceListGETSerializer(serializers.Serializer):
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
        class User(serializers.Serializer):
            type = serializers.CharField(),
            id = serializers.IntegerField()

        class ReferenceRequest(serializers.Serializer):
            type = serializers.CharField()
            id = serializers.IntegerField()

        user = data_wrapped(User)(required=True)
        reference_request = data_wrapped(ReferenceRequest)(required=False, allow_null=True)

    id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=True)
    attributes = Attributes()
    relationships = Relationships()


class ReferencePATCHQuerySerializer(serializers.Serializer):
    class PATCHQueryAttributes(serializers.ModelSerializer):
        class Meta:
            model = Reference
            fields = ('priority', 'comment', 'reference_link', 'reference_link_title')

    type = serializers.CharField(required=True)
    attributes = PATCHQueryAttributes()


class ReferenceReportQuerySerializer(serializers.Serializer):
    class ReferenceReportQueryAttributes(serializers.ModelSerializer):
        class Meta:
            model = ReferenceReport
            fields = ('reason', 'comment')

    type = serializers.CharField(required=True)
    attributes = ReferenceReportQueryAttributes()


class ReferenceReportSerializer(ReferenceReportQuerySerializer):
    class ReferenceReportAttributes(ReferenceReportQuerySerializer.ReferenceReportQueryAttributes):
        pass

    class ReferenceReportRelationships(serializers.Serializer):
        class User(serializers.Serializer):
            type = serializers.CharField()
            id = serializers.IntegerField()

        class Reference(serializers.Serializer):
            type = serializers.CharField()
            id = serializers.IntegerField()

        user = data_wrapped(User)(required=True, allow_null=True)
        reference = data_wrapped(Reference)(required=True, allow_null=True)

    id = serializers.IntegerField(required=True)
    relationships = ReferenceReportRelationships()
    attributes = ReferenceReportAttributes()
