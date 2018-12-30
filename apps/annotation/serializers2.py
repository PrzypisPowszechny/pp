import copy
import json

import inflection
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import _UnvalidatedField

from apps.annotation.utils import standardize_url
from .models import Annotation, AnnotationUpvote


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
        value = getattr(self.context['root_resource_obj'], 'id', None) or self.context['root_resource_obj']
        value = super().to_representation(value)
        return str(value)


class ConstField(serializers.Field):
    default_error_messages = {
        'non_equal': "value is not equal to constant",
    }

    def __init__(self, const_value=None, **kwargs):
        kwargs['source'] = '*'
        self.const_value = const_value
        super(ConstField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if data is not self.const_value:
            self.fail('non_equal', input=data)
        return data

    def to_representation(self, value):
        return self.const_value


class CamelcaseConstField(ConstField):
    def to_internal_value(self, data):
        return inflection.underscore(super().to_internal_value(data))

    def to_representation(self, value):
        value = super().to_representation(value)
        return inflection.camelize(value, uppercase_first_letter=False)


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


class StandardizedRepresentationURLField(serializers.URLField):
    def to_representation(self, value):
        return standardize_url(value)


class LinkSerializerMethodField(serializers.SerializerMethodField, serializers.URLField):
    pass


class RootLinksSerializer(serializers.Serializer):
    self = LinkSerializerMethodField(read_only=True)

    def __init__(self, self_link_url_name,  *args, **kwargs):
        kwargs['source'] = '*'
        super().__init__(*args, **kwargs)
        self.self_link_url_name = self_link_url_name

    def get_self(self, instance):
        root_obj = getattr(self.context['root_resource_obj'], 'id', None) or self.context['root_resource_obj']
        obj_id = getattr(root_obj, 'id', None) or root_obj
        return self.context['request'].build_absolute_uri(reverse(self.self_link_url_name, args=(obj_id,)))


class ResourceField(serializers.Field):

    type_class = CamelcaseConstField
    id_class = IDField

    def __init__(self, resource_name, **kwargs):
        # This is cons for `type` ConstField
        self.type_subfield = self.type_class(const_value=resource_name)
        self.id_subfield = self.id_class()
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        self.type_subfield.run_validation(data.get('type', None))
        value = self.id_subfield.run_validation(data.get('id', None))
        return value

    def to_representation(self, value):
        return {
            'type': self.type_subfield.to_representation(None),
            'id': self.id_subfield.to_representation(value)
        }


# Universal constant for marking the value of none relation (which does not mean whole output of field is =None).
# It does not change reference even if called (as class-based const does).
relation_none = lambda: relation_none


class RelationField(serializers.Field):

    child = _UnvalidatedField()

    default_error_messages = {
        'data_missing': "'data' key is missing",
        'not_a_dict': _('Expected a dictionary of items but got type "{input_type}".'),
    }

    def __init__(self, related_link_url_name, many=False, **kwargs):
        self.related_link_url_name = related_link_url_name
        self.child = kwargs.pop('child', copy.deepcopy(self.child))
        self.many = many
        kwargs.setdefault('default', relation_none)

        if self.many:
            self.child = serializers.ListField(child=self.child, default=[])
        self.child.bind(field_name='', parent=self)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            self.fail('not_a_dict', input_type=type(data).__name__)
        if 'data' not in data:
            self.fail('data_missing')
        return self.child.run_validation(data['data'])

    def to_representation(self, instance):
        root_obj_id = getattr(self.context['root_resource_obj'], 'id', None) or self.context['root_resource_obj']

        if instance is relation_none:
            data_value = [] if self.many else None
        else:
            data_value = self.child.to_representation(instance)

        return {
            'data': data_value,
            'links': {
                'related': self.context['request'].build_absolute_uri(
                    reverse(self.related_link_url_name, args=(root_obj_id,))
                )
            }
        }

    def get_attribute(self, instance):
        attribute = super().get_attribute(instance)
        # If we don't set to `relation_none`, parent serializer just uses None instead of allowing us to handle that
        if attribute is None:
            return relation_none
        return attribute
    

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
        user = RelationField(
            related_link_url_name='api:annotation_related_user',
            child=ResourceField(resource_name='users')
        )
        annotation_upvote = RelationField(
            related_link_url_name='api:annotation_related_upvote',
            child=ResourceField(resource_name='annotation_upvotes'),
        )
        annotation_reports = RelationField(
            many=True,
            related_link_url_name='api:annotation_related_reports',
            child=ResourceField(resource_name='annotation_reports')
        )

    id = RootIDField()
    type = CamelcaseConstField('annotations')
    links = RootLinksSerializer(self_link_url_name='api:annotation')
    attributes = Attributes()
    relationships = Relationships()
