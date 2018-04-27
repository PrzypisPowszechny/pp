from django.urls import reverse
from rest_framework import serializers

from apps.pp.models import AnnotationReport
from .models import Annotation, AnnotationUpvote


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


# Annotation

class AnnotationDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False)

        class Meta:
            model = Annotation
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'annotation_link', 'annotation_link_title')

    attributes = Attributes()


class AnnotationSerializer(ResourceSerializer, AnnotationDeserializer):
    class Attributes(AnnotationDeserializer.Attributes):
        upvote_count = serializers.SerializerMethodField()
        upvote = serializers.SerializerMethodField('is_upvote')
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = AnnotationDeserializer.Attributes.Meta.model

            fields = AnnotationDeserializer.Attributes.Meta.fields + (
                'upvote', 'upvote_count', 'does_belong_to_user',
            )

        @property
        def request_user(self):
            return self.context['request'].user if self.context.get('request') else None

        def get_upvote_count(self, instance):
            assert self.request_user is not None
            return AnnotationUpvote.objects.filter(user=self.request_user, annotation=instance) \
                .count()

        def is_upvote(self, instance):
            assert self.request_user is not None
            return AnnotationUpvote.objects.filter(user=self.request_user, annotation=instance) \
                .exists()

        def get_does_belong_to_user(self, instance):
            assert self.request_user is not None
            return self.request_user.id == instance.user_id

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:annotation_related_user'

        class Upvote(RelationSerializer):
            related_link_url_name = 'api:annotation_related_upvote'

        class AnnotationReports(RelationManySerializer):
            related_link_url_name = 'api:annotation_related_reports'

        user = User(required=True)
        upvote = Upvote()
        reports = AnnotationReports()

    attributes = Attributes()
    relationships = Relationships()


class AnnotationListSerializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        upvote_count = serializers.IntegerField(default=0)
        upvote = serializers.BooleanField(default=False)
        does_belong_to_user = serializers.BooleanField(default=False)

        class Meta:
            model = Annotation
            fields = ('url', 'ranges', 'quote',
                      'priority', 'comment', 'annotation_link', 'annotation_link_title',
                      'upvote', 'upvote_count',
                      'does_belong_to_user',
                      )
            read_only_fields = ('upvote', 'upvote_count',
                                'does_belong_to_user')

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:annotation_related_user'

        class Upvote(RelationSerializer):
            related_link_url_name = 'api:annotation_related_upvote'

        class AnnotationReports(RelationManySerializer):
            related_link_url_name = 'api:annotation_related_reports'

        user = User(required=True)
        upvote = Upvote()
        reports = AnnotationReports()

    class Links(ResourceLinksSerializer):
        self_link_url_name = 'api:annotation'

    attributes = Attributes()
    relationships = Relationships()
    links = Links()


class AnnotationPatchDeserializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = Annotation
            fields = ('priority', 'comment', 'annotation_link', 'annotation_link_title')

    attributes = Attributes()

# Report

class AnnotationReportDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')

    class Relationships(serializers.Serializer):
        class Annotation(RelationDeserializer):
            pass

        annotation = Annotation()

    attributes = Attributes()
    relationships = Relationships()


class AnnotationReportSerializer(ResourceSerializer, AnnotationReportDeserializer):
    class Relationships(serializers.Serializer):
        class Annotation(RelationSerializer):
            related_link_url_name = 'api:annotation_report_related_annotation'

        annotation = Annotation()

    relationships = Relationships()


# Upvote

class AnnotationUpvoteDeserializer(ResourceTypeSerializer):
    class Relationships(serializers.Serializer):
        class Annotation(RelationDeserializer):
            pass

        annotation = Annotation()

    relationships = Relationships()


class AnnotationUpvoteSerializer(ResourceSerializer):
    class Relationships(serializers.Serializer):
        class Annotation(RelationSerializer):
            related_link_url_name = 'api:annotation_upvote_related_annotation'

        annotation = Annotation()

    relationships = Relationships()


# User

class UserSerializer(ResourceSerializer):
    class Attributes(serializers.Serializer):
        pass

    attributes = Attributes()
