from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import AnnotationReport, AnnotationRequest
from apps.api import fields
from .models import Annotation, AnnotationUpvote


class RequestMixin:
    def _assert_request(self):
        assert 'request' in self.context, f"No request in context of {self.__class__.__name__}"

    @property
    def request_user(self):
        self._assert_request()
        return self.context['request'].user


class ResourceLinksSerializer(serializers.Serializer):
    self = fields.LinkSerializerMethodField(read_only=True)

    def __init__(self, self_link_url_name, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)
        self.self_link_url_name = self_link_url_name

    def get_self(self, instance):
        obj_id = getattr(instance, 'id', None) or instance
        return self.context['request'].build_absolute_uri(reverse(self.self_link_url_name, args=[obj_id]))


# Annotation

class AnnotationSerializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer, RequestMixin):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
        quote = serializers.CharField()
        # TODO: this will be required soon
        quote_context = serializers.CharField(required=False, allow_blank=True)
        comment = serializers.CharField(required=False, allow_blank=True)

        publisher = serializers.CharField()
        upvote_count_except_user = serializers.SerializerMethodField()
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = Annotation

            fields = ('url', 'range', 'quote', 'quote_context',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title',

                      'publisher', 'create_date', 'upvote_count_except_user', 'does_belong_to_user')

        def get_upvote_count_except_user(self, instance):
            return AnnotationUpvote.objects.filter(annotation=instance).exclude(user=self.request_user).count()

        def get_does_belong_to_user(self, instance):
            return self.request_user.id == instance.user_id

    class Relationships(serializers.Serializer):
        user = fields.RelationField(
            related_link_url_name='api:annotation:annotation_related_user',
            child=fields.ResourceField(resource_name='users')
        )
        annotation_request = fields.RelationField(
            child=fields.ResourceField('annotation_requests'),
        )
        annotation_upvote = fields.RelationField(
            related_link_url_name='api:annotation:annotation_related_upvote',
            child=fields.ResourceField(resource_name='annotation_upvotes'),
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotations')
    links = ResourceLinksSerializer(source='id', self_link_url_name='api:annotation:annotation')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationListSerializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
        quote = serializers.CharField()
        quote_context = serializers.CharField()
        publisher = serializers.CharField()
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
        user = fields.RelationField(
            related_link_url_name='api:annotation:annotation_related_user',
            child=fields.ResourceField(resource_name='users')
        )
        annotation_request = fields.RelationField(
            child=fields.ResourceField('annotation_requests'),
        )
        annotation_upvote = fields.RelationField(
            related_link_url_name='api:annotation:annotation_related_upvote',
            child=fields.ResourceField(resource_name='annotation_upvotes'),
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotations')
    links = ResourceLinksSerializer(source='id', self_link_url_name='api:annotation:annotation')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
        quote = serializers.CharField()
        # TODO: this will be required soon
        quote_context = serializers.CharField(required=False, allow_blank=True)
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('url', 'range', 'quote', 'quote_context',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    class Relationships(serializers.Serializer):
        annotation_request = fields.RelationField(
            child=fields.ResourceField('annotation_requests'),
            required=False
        )

    type = fields.CamelcaseConstField('annotations')
    attributes = Attributes()
    relationships = Relationships(required=False)


class AnnotationPatchDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('pp_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotations')
    attributes = Attributes()


# Report

class AnnotationReportSerializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')
            extra_kwargs = {'comment': {'required': False, 'allow_blank': True}}

    class Relationships(serializers.Serializer):
        annotation = fields.RelationField(
            child=fields.ResourceField('annotations')
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotation_reports')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationReportDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')
            extra_kwargs = {'comment': {'required': False, 'allow_blank': True}}

        def validate(self, data):
            if data.get('reason') is SUGGESTED_CORRECTION and not data.get('comment'):
                raise ValidationError({
                    'comment': 'Comment is required for report "%s" reason' % SUGGESTED_CORRECTION}
                )
            return data

    class Relationships(serializers.Serializer):
        annotation = fields.RelationField(
            child=fields.ResourceField('annotations')
        )

    type = fields.CamelcaseConstField('annotation_reports')
    attributes = Attributes()
    relationships = Relationships()


# Upvote

class AnnotationUpvoteDeserializer(serializers.Serializer):
    class Relationships(serializers.Serializer):
        annotation = fields.RelationField(
            child=fields.ResourceField('annotations')
        )

    type = fields.CamelcaseConstField('annotation_upvotes')
    relationships = Relationships()


class AnnotationUpvoteSerializer(serializers.Serializer):
    class Relationships(serializers.Serializer):
        annotation = fields.RelationField(
            child=fields.ResourceField('annotations')
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotation_upvotes')
    relationships = Relationships()


# User

class UserSerializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        pass

    attributes = Attributes()

    id = fields.IDField()
    type = fields.CamelcaseConstField('users')


# Annotation request

class AnnotationRequestDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()

        class Meta:
            model = AnnotationRequest
            fields = ('url', 'quote', 'comment', 'notification_email')

    type = fields.CamelcaseConstField('annotation_requests')
    attributes = Attributes()


class AnnotationRequestSerializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer, RequestMixin):
        url = fields.StandardizedRepresentationURLField()
        requested_by_user = serializers.SerializerMethodField()

        class Meta:
            model = AnnotationRequest
            fields = ('url', 'quote', 'comment', 'notification_email', 'create_date', 'requested_by_user')

        def get_requested_by_user(self, instance) -> bool:
            return self.request_user.id == instance.user_id

    class Relationships(serializers.Serializer):
        annotations = fields.RelationField(
            child=fields.ResourceField('annotations'),
            many=True,
            required=False
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotation_requests')
    attributes = Attributes()
    relationships = Relationships()
