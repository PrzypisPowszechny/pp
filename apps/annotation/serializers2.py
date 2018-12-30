import json

import inflection
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import AnnotationReport, AnnotationRequest
from apps.annotation.utils import standardize_url
from .models import Annotation, AnnotationUpvote


# Resource

class IDField(serializers.IntegerField):
    def to_representation(self, value):
        value = getattr(value, 'id', None) or value
        value = super().to_representation(value)
        return str(value)


class RootIDField(IDField):
    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def to_representation(self, value):
        value = getattr(self.context['root_obj'], 'id', None) or self.context['root_obj']
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


class ConstField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        super(ConstField, self).__init__(**kwargs)

    # TODO: validation

    def to_representation(self, value):
        return getattr(self.parent, self.field_name.upper())


class TypeConstField(ConstField):
    def to_internal_value(self, data):
        return inflection.underscore(data)

    def to_representation(self, value):
        value = super(TypeConstField, self).to_representation(value)
        return value[0].lower() + inflection.camelize(value)[1:]


class StandardizedRepresentationURLField(serializers.URLField):
    def to_representation(self, value):
        return standardize_url(value)


class ResourceIdSerializer(serializers.Serializer):
    id = IDField()


class LinkField(serializers.SerializerMethodField, serializers.URLField):
    pass


# Relation


class RootLinksSerializer(serializers.Serializer):
    self = LinkField()
    self_link_url_name = None

    def __init__(self, self_link_url_name,  *args, **kwargs):
        kwargs['source'] = '*'
        super().__init__(*args, **kwargs)
        self.self_link_url_name = self_link_url_name

    def get_self(self, instance):
        root_obj = getattr(self.context['root_obj'], 'id', None) or self.context['root_obj']
        obj_id = getattr(root_obj, 'id', None) or root_obj
        return self.context['request'].build_absolute_uri(reverse(self.self_link_url_name, args=(obj_id,)))


class RelationLinksSerializer(serializers.Serializer):
    related = LinkField()
    related_link_url_name = None

    def __init__(self, related_link_url_name,  *args, **kwargs):
        kwargs['source'] = '*'
        super().__init__(*args, **kwargs)
        self.related_link_url_name = related_link_url_name

    def get_related(self, instance):
        root_obj = getattr(self.context['root_obj'], 'id', None) or self.context['root_obj']
        obj_id = getattr(root_obj, 'id', None) or root_obj
        return self.context['request'].build_absolute_uri(reverse(self.related_link_url_name, args=(obj_id,)))


class ResourceField(serializers.Serializer):
    def __init__(self, resource_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TYPE = resource_name

    type = TypeConstField()
    id = IDField()

    def to_representation(self, instance):
        """
        This field is in fact composed of constant and id, so pass instance value (which should be id in fact)
        to the id field.
        """
        return super(ResourceField, self).to_representation({'id': instance})


class AnnotationSerializer(serializers.Serializer):

    class Attributes(serializers.ModelSerializer):
        url = StandardizedRepresentationURLField()
        range = ObjectField(json_internal_type=True)
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
        class User(serializers.Serializer):
            data = ResourceField(resource_name='users')
            links = RelationLinksSerializer(related_link_url_name='api:annotation_related_user')

        class Upvote(serializers.Serializer):
            data = ResourceField(resource_name='annotation_upvotes')
            links = RelationLinksSerializer(related_link_url_name='api:annotation_related_upvote')

        class Reports(serializers.Serializer):
            data = ResourceField(resource_name='annotation_reports', many=True)
            links = RelationLinksSerializer(related_link_url_name='api:annotation_related_reports')

        user = User()
        annotation_upvote = Upvote()
        annotation_reports = Reports()

    id = RootIDField()
    type = TypeConstField()
    TYPE = 'annotations'
    links = RootLinksSerializer(self_link_url_name='api:annotation')
    attributes = Attributes()
    relationships = Relationships()
