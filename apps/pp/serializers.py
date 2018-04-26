from django.urls import reverse
from rest_framework import serializers

from apps.pp.models import ReferenceReport
from apps.pp.utils import data_wrapped
from .models import Reference, UserReferenceFeedback


# Resource

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


# Relation

class ResourceLinksSerializer(serializers.Serializer):
    self = LinkField()
    self_link_url_name = None

    def get_self(self, instance):
        obj_id = getattr(instance, 'id', None) or instance
        return reverse(self.self_link_url_name, args=(obj_id,))


class RelationLinksSerializer(serializers.Serializer):
    related = LinkField()
    related_link_url_name = None

    def get_related(self, instance):
        serializer = self
        related_link_url_name = getattr(serializer, 'related_link_url_name', None)
        while related_link_url_name is None and serializer.parent is not None:
            serializer = serializer.parent
            related_link_url_name = getattr(serializer, 'related_link_url_name', None)
        assert related_link_url_name is not None, \
            "%s requires at least one parent to set related_link_url_name" % RelationLinksSerializer.__name__

        obj_id = getattr(instance, 'id', None) or instance
        return reverse(related_link_url_name, args=(obj_id,))


class RelationDeserializer(serializers.Serializer):
    data = ResourceSerializer(required=False)


class RelationSerializer(RelationDeserializer):
    related_link_url_name = None
    links = RelationLinksSerializer(required=True)


class RelationManyDeserializer(serializers.Serializer):
    data = ResourceSerializer(required=False, many=True)


class RelationManySerializer(RelationManyDeserializer):
    related_link_url_name = None
    links = RelationLinksSerializer(required=True)


# Reference

class ReferenceDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title')

    attributes = Attributes()


class ReferenceSerializer(ResourceSerializer, ReferenceDeserializer):
    class Attributes(ReferenceDeserializer.Attributes):
        useful_count = serializers.SerializerMethodField()
        useful = serializers.SerializerMethodField('is_useful')
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = ReferenceDeserializer.Attributes.Meta.model

            fields = ReferenceDeserializer.Attributes.Meta.fields + (
                'useful', 'useful_count', 'does_belong_to_user',
            )

        @property
        def request_user(self):
            return self.context['request'].user if self.context.get('request') else None

        def get_useful_count(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance) \
                .count()

        def is_useful(self, instance):
            assert self.request_user is not None
            return UserReferenceFeedback.objects.filter(user=self.request_user, reference=instance) \
                .exists()

        def get_does_belong_to_user(self, instance):
            assert self.request_user is not None
            return self.request_user.id == instance.user_id

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:reference_user'

        class Useful(RelationSerializer):
            related_link_url_name = 'api:reference_useful'

        class ReferenceReports(RelationManySerializer):
            related_link_url_name = 'api:reference_reports'

        user = User(required=True)
        useful = Useful()
        reference_reports = ReferenceReports()

    attributes = Attributes()
    relationships = Relationships()


class ReferenceListSerializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        useful_count = serializers.IntegerField(default=0)
        useful = serializers.BooleanField(default=False)
        does_belong_to_user = serializers.BooleanField(default=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title',
                      'useful', 'useful_count',
                      'does_belong_to_user',
                      )
            read_only_fields = ('useful', 'useful_count',
                                'does_belong_to_user')

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:reference_user'

        class Useful(RelationSerializer):
            related_link_url_name = 'api:reference_useful'

        class ReferenceReports(RelationManySerializer):
            related_link_url_name = 'api:reference_reports'

        user = User(required=True)
        useful = Useful()
        reference_reports = ReferenceReports()

    class Links(ResourceLinksSerializer):
        self_link_url_name = 'api:reference'

    attributes = Attributes()
    relationships = Relationships()
    links = Links()


class ReferencePatchDeserializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = Reference
            fields = ('priority', 'comment', 'reference_link', 'reference_link_title')

    attributes = Attributes()

# Report

class ReferenceReportDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = ReferenceReport
            fields = ('reason', 'comment')

    class Relationships(serializers.Serializer):
        class Reference(RelationDeserializer):
            pass

        reference = Reference()

    attributes = Attributes()
    relationships = Relationships()


class ReferenceReportSerializer(ResourceSerializer, ReferenceReportDeserializer):
    class Relationships(serializers.Serializer):
        class Reference(RelationSerializer):
            related_link_url_name = 'api:report_reference'

        reference = Reference()

    relationships = Relationships()


# Feedback

class FeedbackDeserializer(ResourceTypeSerializer):
    class Relationships(serializers.Serializer):
        class Reference(RelationDeserializer):
            pass

        reference = Reference()

    relationships = Relationships()


class FeedbackSerializer(ResourceSerializer):
    """
    Used only for introspection purposes by schema generator.

    Should be same as Useful and Objection serializers with only exception to link parameter.
    """
    class Relationships(serializers.Serializer):
        class Reference(RelationSerializer):
            pass

        reference = Reference()

    relationships = Relationships()


class UsefulSerializer(ResourceSerializer):
    class Relationships(serializers.Serializer):
        class Reference(RelationSerializer):
            related_link_url_name = 'api:useful_reference'

        reference = Reference()

    relationships = Relationships()


# User

class UserSerializer(ResourceSerializer):
    class Attributes(serializers.Serializer):
        pass

    attributes = Attributes()
