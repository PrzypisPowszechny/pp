import json

import inflection
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import AnnotationReport
from apps.annotation.utils import standardize_url
from .models import Annotation, AnnotationUpvote


# Resource

class IDField(serializers.IntegerField):
    def to_representation(self, value):
        value = super().to_representation(value)
        return str(value)


class ObjectField(serializers.Field):
    default_error_messages = {
        'invalid': _('Value must be a valid object that can be JSON serialized')
    }
    initial = {}

    def __init__(self, *args, **kwargs):
        self.json_internal_type = kwargs.pop('json_internal_type', False)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            json_data = json.dumps(data)
        except (TypeError, ValueError):
            self.fail('invalid')
        return json_data if self.json_internal_type else data

    def to_representation(self, value):
        if value is None or value == "":
            return None
        if self.json_internal_type:
            return json.loads(value)
        return value


class TypeField(serializers.CharField):
    def to_internal_value(self, data):
        return inflection.underscore(data)

    def to_representation(self, value):
        return value[0].lower() + inflection.camelize(value)[1:]


class StandardizedRepresentationURLField(serializers.URLField):
    def to_representation(self, value):
        return standardize_url(value)


# Serializer used purely for schema generation
# When inherited from no additional 'data' root is added form more control over the generated schema
class SchemaGeneratorSerializer(serializers.Serializer):
    pass

class ResourceIdSerializer(serializers.Serializer):
    id = IDField(required=True)


class ResourceTypeSerializer(serializers.Serializer):
    type = TypeField(required=True)


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
        return self.context['request'].build_absolute_uri(reverse(self.self_link_url_name, args=(obj_id,)))


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
        return self.context['request'].build_absolute_uri(reverse(related_link_url_name, args=(obj_id,)))


class RelationDeserializer(serializers.Serializer):
    data = ResourceSerializer(required=True)


class NullableRelationDeserializer(serializers.Serializer):
    """
    For relations which are optional, then data must be present but can be null
    """
    data = ResourceSerializer(required=True, allow_null=True)


class RelationSerializer(serializers.Serializer):
    data = ResourceSerializer(required=True, allow_null=True)
    related_link_url_name = None
    links = RelationLinksSerializer(required=True)


class RelationManySerializer(serializers.Serializer):
    data = ResourceSerializer(required=True, many=True)
    related_link_url_name = None
    links = RelationLinksSerializer(required=True)


# Annotation

class AnnotationDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        url = StandardizedRepresentationURLField()
        range = ObjectField(json_internal_type=True)
        quote = serializers.CharField(required=True)
        # TODO: this will be required soon
        quote_context = serializers.CharField(required=False, allow_blank=True)
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('url', 'range', 'quote', 'quote_context',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    attributes = Attributes()


class AnnotationSerializer(ResourceSerializer, AnnotationDeserializer):
    class Attributes(AnnotationDeserializer.Attributes):
        publisher = serializers.CharField(required=True)
        upvote_count_except_user = serializers.SerializerMethodField()
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = AnnotationDeserializer.Attributes.Meta.model

            fields = AnnotationDeserializer.Attributes.Meta.fields + (
                'publisher', 'create_date', 'upvote_count_except_user', 'does_belong_to_user',
            )

        @property
        def request_user(self):
            return self.context['request'].user if self.context.get('request') else None

        def get_upvote_count_except_user(self, instance):
            assert self.request_user is not None
            return AnnotationUpvote.objects.filter(annotation=instance).exclude(user=self.request_user).count()

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
        annotation_upvote = Upvote()
        annotation_reports = AnnotationReports()

    attributes = Attributes()
    relationships = Relationships()


class AnnotationListSerializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        url = StandardizedRepresentationURLField()
        range = ObjectField(json_internal_type=True)
        quote = serializers.CharField(required=True)
        quote_context = serializers.CharField()
        publisher = serializers.CharField(required=True)
        upvote_count_except_user = serializers.IntegerField(default=0)
        does_belong_to_user = serializers.BooleanField(default=False)

        class Meta:
            model = Annotation
            fields = ('url', 'range', 'quote', 'quote_context', 'publisher',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title',
                      'create_date', 'upvote_count_except_user', 'does_belong_to_user',
                      )
            read_only_fields = ('upvote_count_except_user',
                                'does_belong_to_user')

    class Relationships(serializers.Serializer):
        class User(RelationSerializer):
            related_link_url_name = 'api:annotation_related_user'

        class Upvote(RelationSerializer):
            related_link_url_name = 'api:annotation_related_upvote'

        class AnnotationReports(RelationManySerializer):
            related_link_url_name = 'api:annotation_related_reports'

        user = User(required=True)
        annotation_upvote = Upvote()
        annotation_reports = AnnotationReports()

    class Links(ResourceLinksSerializer):
        self_link_url_name = 'api:annotation'

    attributes = Attributes()
    relationships = Relationships()
    links = Links()


class AnnotationPatchDeserializer(ResourceSerializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('pp_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    attributes = Attributes()


# Report

class AnnotationReportDeserializer(ResourceTypeSerializer):
    class Attributes(serializers.ModelSerializer):
        def validate(self, data):
            if data.get('reason') is SUGGESTED_CORRECTION and not data.get('comment'):
                raise ValidationError({
                    'comment': 'Comment is required for report "%s" reason' % SUGGESTED_CORRECTION}
                )
            return data

        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')
            extra_kwargs = {'comment': {'required': False, 'allow_blank': True}}

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

# Annotation request

class AnnotationRequestDeserializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        url = StandardizedRepresentationURLField()
        quote = serializers.CharField(required=False, allow_blank=True)

    attributes = Attributes()
