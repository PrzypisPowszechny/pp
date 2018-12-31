from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.annotation import fields
from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import AnnotationReport, AnnotationRequest
from .models import Annotation, AnnotationUpvote


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

    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
        quote = serializers.CharField(required=True)
        # TODO: this will be required soon
        quote_context = serializers.CharField(required=False, allow_blank=True)
        comment = serializers.CharField(required=False, allow_blank=True)

        publisher = serializers.CharField(required=True)
        upvote_count_except_user = serializers.SerializerMethodField()
        does_belong_to_user = serializers.SerializerMethodField()

        class Meta:
            model = Annotation

            fields = ('url', 'range', 'quote', 'quote_context',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title',

                      'publisher', 'create_date', 'upvote_count_except_user', 'does_belong_to_user')

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
        user = fields.RelationField(
            related_link_url_name='api:annotation_related_user',
            child=fields.ResourceField(resource_name='users')
        )
        annotation_upvote = fields.RelationField(
            related_link_url_name='api:annotation_related_upvote',
            child=fields.ResourceField(resource_name='annotation_upvotes'),
        )
        annotation_reports = fields.RelationField(
            many=True,
            related_link_url_name='api:annotation_related_reports',
            child=fields.ResourceField(resource_name='annotation_reports')
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotations')
    links = ResourceLinksSerializer(source='id', self_link_url_name='api:annotation')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationListSerializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
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
        user = fields.RelationField(
            related_link_url_name='api:annotation_related_user',
            child=fields.ResourceField(resource_name='users')
        )
        annotation_upvote = fields.RelationField(
            related_link_url_name='api:annotation_related_upvote',
            child=fields.ResourceField(resource_name='annotation_upvotes'),
        )
        annotation_reports = fields.RelationField(
            many=True,
            related_link_url_name='api:annotation_related_reports',
            child=fields.ResourceField(resource_name='annotation_reports')
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotations')
    links = ResourceLinksSerializer(source='id', self_link_url_name='api:annotation')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        url = fields.StandardizedRepresentationURLField()
        range = fields.ObjectField(json_internal_type=True)
        quote = serializers.CharField(required=True)
        # TODO: this will be required soon
        quote_context = serializers.CharField(required=False, allow_blank=True)
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('url', 'range', 'quote', 'quote_context',
                      'pp_category', 'demagog_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    type = fields.CamelcaseConstField('annotations')
    attributes = Attributes()


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
            related_link_url_name='api:annotation_report_related_annotation',
            child=fields.ResourceField('annotations')
        )

    type = fields.CamelcaseConstField('annotation_reports')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationReportSerializer(serializers.Serializer):

    class Attributes(serializers.ModelSerializer):
        class Meta:
            model = AnnotationReport
            fields = ('reason', 'comment')
            extra_kwargs = {'comment': {'required': False, 'allow_blank': True}}

    class Relationships(serializers.Serializer):

        annotation = fields.RelationField(
            related_link_url_name='api:annotation_report_related_annotation',
            child=fields.ResourceField('annotations')
        )

    id = fields.IDField()
    type = fields.CamelcaseConstField('annotation_reports')
    attributes = Attributes()
    relationships = Relationships()

#
# # Upvote
#
# class AnnotationUpvoteDeserializer(ResourceTypeSerializer):
#     class Relationships(serializers.Serializer):
#         class Annotation(RelationDeserializer):
#             pass
#
#         annotation = Annotation()
#
#     relationships = Relationships()
#
#
# class AnnotationUpvoteSerializer(ResourceSerializer):
#     class Relationships(serializers.Serializer):
#         class Annotation(RelationSerializer):
#             related_link_url_name = 'api:annotation_upvote_related_annotation'
#
#         annotation = Annotation()
#
#     relationships = Relationships()
#
#
# # User
#
# class UserSerializer(ResourceSerializer):
#     class Attributes(serializers.Serializer):
#         pass
#
#     attributes = Attributes()
#
# # Annotation request
#
# class AnnotationRequestDeserializer(ResourceTypeSerializer):
#     class Attributes(serializers.ModelSerializer):
#         url = StandardizedRepresentationURLField()
#
#         class Meta:
#             model = AnnotationRequest
#             fields = ('url', 'quote', 'comment', 'notification_email')
#
#     attributes = Attributes()
#
# class AnnotationRequestSerializer(ResourceSerializer, AnnotationRequestDeserializer):
#
#     class Attributes(AnnotationRequestDeserializer.Attributes):
#         class Meta:
#             model = AnnotationRequestDeserializer.Attributes.Meta.model
#
#             fields = AnnotationRequestDeserializer.Attributes.Meta.fields
#
#     attributes = Attributes()
