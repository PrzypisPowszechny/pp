from django.urls import reverse
from rest_framework import serializers

from apps.pp.models import AnnotationReport
from apps.pp.utils import data_wrapped
from .models import Reference, AnnotationUpvote


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
        upvote_count = serializers.SerializerMethodField()
        upvote = serializers.SerializerMethodField('is_upvote')
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = ReferenceDeserializer.Attributes.Meta.model

            fields = ReferenceDeserializer.Attributes.Meta.fields + (
                'upvote', 'upvote_count', 'does_belong_to_user',
            )

        @property
        def request_user(self):
            return self.context['request'].user if self.context.get('request') else None

        def get_upvote_count(self, instance):
            assert self.request_user is not None
            return AnnotationUpvote.objects.filter(user=self.request_user, reference=instance) \
                .count()

        def is_upvote(self, instance):
            assert self.request_user is not None
            return AnnotationUpvote.objects.filter(user=self.request_user, reference=instance) \
                .exists()

        def get_does_belong_to_user(self, instance):
            assert self.request_user is not None
            return self.request_user.id == instance.user_id

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:reference_user'

        class Upvote(RelationSerializer):
            related_link_url_name = 'api:annotation_upvote'

        class AnnotationReports(RelationManySerializer):
            related_link_url_name = 'api:annotation_reports'

        user = User(required=True)
        upvote = Upvote()
        annotation_reports = AnnotationReports()

    attributes = Attributes()
    relationships = Relationships()


class ReferenceListSerializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        upvote_count = serializers.IntegerField(default=0)
        upvote = serializers.BooleanField(default=False)
        does_belong_to_user = serializers.BooleanField(default=False)

        class Meta:
            model = Reference
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'reference_link', 'reference_link_title',
                      'upvote', 'upvote_count',
                      'does_belong_to_user',
                      )
            read_only_fields = ('upvote', 'upvote_count',
                                'does_belong_to_user')

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:reference_user'

        class Upvote(RelationSerializer):
            related_link_url_name = 'api:annotation_upvote'

        class AnnotationReports(RelationManySerializer):
            related_link_url_name = 'api:annotation_reports'

        user = User(required=True)
        upvote = Upvote()
        annotation_reports = AnnotationReports()

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

class AnnotationReportDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')

    class Relationships(serializers.Serializer):
        class Reference(RelationDeserializer):
            pass

        reference = Reference()

    attributes = Attributes()
    relationships = Relationships()


class AnnotationReportSerializer(ResourceSerializer, AnnotationReportDeserializer):
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

    Should be same as Upvote and Objection serializers with only exception to link parameter.
    """
    class Relationships(serializers.Serializer):
        class Reference(RelationSerializer):
            pass

        reference = Reference()

    relationships = Relationships()


class UpvoteSerializer(ResourceSerializer):
    class Relationships(serializers.Serializer):
        class Reference(RelationSerializer):
            related_link_url_name = 'api:upvote_reference'

        reference = Reference()

    relationships = Relationships()


# User

class UserSerializer(ResourceSerializer):
    class Attributes(serializers.Serializer):
        pass

    attributes = Attributes()
