from collections import OrderedDict

from django.urls import reverse
from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework_json_api import serializers as serializers_json_api

from apps.pp.models import ReferenceReport
from apps.pp.utils import data_wrapped
from .models import Reference, UserReferenceFeedback


class IDField(serializers.IntegerField):
    def to_representation(self, value):
        value = super().to_representation(value)
        return str(value)


class ResourceIdSerializer(serializers.Serializer):
    id = IDField(required=True)


class ResourceTypeSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)


class ResourceSerializer(ResourceIdSerializer, ResourceTypeSerializer):
    pass


class LinkField(serializers.SerializerMethodField, serializers.URLField):
    pass


class RelationLinksSerializer(serializers.Serializer):
    related = LinkField()

    def get_related(self, instance):
        serializer = self
        while not isinstance(serializer, RelationManySerializer):
            if serializer.parent is None:
                raise AssertionError('%s should be a child of %s serializer' %
                                     self.__class__.__name__,
                                     RelationManySerializer.__name__)
            serializer = serializer.parent
        return reverse(serializer.related_link_url_name, args=(instance,))


class RelationSerializer(serializers.Serializer):
    links = RelationLinksSerializer(required=True)
    data = ResourceSerializer(required=False)


class RelationManySerializer(serializers.Serializer):
    related_link_url_name = None
    links = RelationLinksSerializer(required=True)
    data = ResourceSerializer(required=False, many=True)


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

        reference_request = data_wrapped(required=False, allow_null=True,
                                         wrapped_serializer=ReferenceRequest(required=False, allow_null=True))

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
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, useful=True) \
                .count()

        def get_objection_count(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, objection=True) \
                .count()

        def is_useful(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, useful=True) \
                .exists()

        def is_objection(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance, objection=True) \
                .exists()

        def get_does_belong_to_user(self, instance):
            assert self.request_user is not None
            return self.request_user.id == instance.user_id

    class Relationships(ReferenceDeserializer.Relationships):
        class User(ResourceSerializer):
            pass

        class ReferenceRequest(ResourceSerializer):
            pass

        user = data_wrapped(required=True, wrapped_serializer=User())
        reference_request = data_wrapped(required=True,
                                         wrapped_serializer=ReferenceRequest(required=False, allow_null=True))

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

    # TODO: 1. relationships, as they are now, because the resources they point to are not accessible
    # TODO: 2. objections, usefuls, reports are those which should be included (with endpoint links) in relationships
    class Relationships(serializers.Serializer):
        class User(serializers.Serializer):
            class UserData(ResourceSerializer):
                pass

            class UserLinks(serializers.Serializer):
                related = serializers.URLField(required=True)
            data = UserData()
            # TODO: link available only after we create User endpoint
            # links = UserLinks()

        class ReferenceRequest(serializers.Serializer):
            class ReferenceRequestData(ResourceSerializer):
                pass

            class ReferenceRequestLinks(serializers.Serializer):
                related = serializers.URLField(required=True)
            data = ReferenceRequestData(required=False, allow_null=True)
            # TODO: link available only after we create ReferenceRequest endpoint
            # links = ReferenceRequestLinks(required=False, allow_null=True)

        user = User(required=True)
        reference_request = ReferenceRequest(required=True)
        # objection = RelationSerializer()
        # useful = RelationSerializer()

        class ReportsRelationMany(RelationManySerializer):
            related_link_url_name = 'api:reference_reports'

        reports = ReportsRelationMany()

    class ReferenceLinks(serializers.Serializer):
        self = serializers.URLField(required=True)

    attributes = Attributes()
    relationships = Relationships()
    links = ReferenceLinks()


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

        user = data_wrapped(required=True, wrapped_serializer=User())
        reference = data_wrapped(required=True, wrapped_serializer=Reference())

    relationships = Relationships()
