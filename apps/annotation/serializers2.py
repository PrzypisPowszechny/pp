from django.urls import reverse
from rest_framework import serializers

from apps.annotation import fields
from .models import Annotation, AnnotationUpvote


class RootLinksSerializer(serializers.Serializer):
    self = fields.LinkSerializerMethodField(read_only=True)

    def __init__(self, self_link_url_name,  *args, **kwargs):
        kwargs['source'] = '*'
        super().__init__(*args, **kwargs)
        self.self_link_url_name = self_link_url_name

    def get_self(self, instance):
        root_obj = getattr(self.context['root_resource_obj'], 'id', None) or self.context['root_resource_obj']
        obj_id = getattr(root_obj, 'id', None) or root_obj
        return self.context['request'].build_absolute_uri(reverse(self.self_link_url_name, args=[obj_id]))


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

    id = fields.RootIDField()
    type = fields.CamelcaseConstField('annotations')
    links = RootLinksSerializer(self_link_url_name='api:annotation')
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

    id = fields.RootIDField()
    type = fields.CamelcaseConstField('annotations')
    links = RootLinksSerializer(self_link_url_name='api:annotation')
    attributes = Attributes()
    relationships = Relationships()


class AnnotationPatchDeserializer(serializers.Serializer):
    class Attributes(serializers.ModelSerializer):
        comment = serializers.CharField(required=False, allow_blank=True)

        class Meta:
            model = Annotation
            fields = ('pp_category', 'comment',
                      'annotation_link', 'annotation_link_title')

    attributes = Attributes()

    #id = fields.RootIDField()
    type = fields.CamelcaseConstField('annotations')
