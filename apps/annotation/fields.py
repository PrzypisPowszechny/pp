import copy
import json

import inflection
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import _UnvalidatedField

from apps.annotation.utils import standardize_url


class IDField(serializers.IntegerField):
    def to_representation(self, value):
        value = getattr(value, 'id', None) or value
        value = super().to_representation(value)
        return str(value)


class ConstField(serializers.Field):
    default_error_messages = {
        'non_equal': "value '{input}' is not equal to constant value '{constant_value}'",
    }

    def __init__(self, const_value=None, **kwargs):
        self.const_value = const_value
        super(ConstField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if data != self.const_value:
            self.fail('non_equal', input=data, constant_value=self.const_value)
        return data

    def get_attribute(self, instance):
        """
        We output just const_value, so do not select any attribute.
        """
        return instance

    def to_representation(self, value):
        return self.const_value


class CamelcaseConstField(ConstField):
    def to_internal_value(self, data):
        return super().to_internal_value(inflection.underscore(data))

    def to_representation(self, value):
        return inflection.camelize(super().to_representation(value), uppercase_first_letter=False)


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


class URLNameField(serializers.URLField):

    def __init__(self, url_name, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)
        self.url_name = url_name

    def to_representation(self, instance):
        obj_id = getattr(instance, 'id', None) or instance
        return self.context['request'].build_absolute_uri(reverse(self.url_name, args=[obj_id]))


class LinkSerializerMethodField(serializers.SerializerMethodField, serializers.URLField):
    pass


class ResourceField(serializers.Field):
    type_class = CamelcaseConstField
    id_class = IDField

    def __init__(self, resource_name, **kwargs):
        self.type_subfield = self.type_class(const_value=resource_name)
        self.type_subfield.bind(field_name='', parent=self)
        self.id_subfield = self.id_class()
        self.id_subfield.bind(field_name='', parent=self)
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
    link_child_class = URLNameField

    default_error_messages = {
        'data_missing': "'data' key is missing",
        'not_a_dict': _('Expected a dictionary of items but got type "{input_type}".'),
    }

    def __init__(self, related_link_url_name, many=False, **kwargs):
        self.related_link_url_name = related_link_url_name
        self.child = kwargs.pop('child', copy.deepcopy(self.child))
        self.link_child = self.link_child_class(url_name=related_link_url_name)
        self.many = many

        if self.many:
            self.child = serializers.ListField(child=self.child)
        self.child.bind(field_name='', parent=self)
        self.link_child.bind(field_name='', parent=self)
        super().__init__(**kwargs)

    def get_default(self):
        default = super().get_default()
        # relation_none -> None
        # The internal value for relation_none is None.
        if default is relation_none:
            return [] if self.many else None
        return default

    def get_attribute(self, instance):
        attribute = super().get_attribute(instance)
        # None -> relation_none
        # Attribute is not missing, but it's None, so we want to set none-relation instead, which outputs more than None
        # value. To do that we override attribute with `relation_none`, so that we can add proper representation later.
        if attribute is None:
            return relation_none
        return attribute

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
                'related': self.link_child.to_representation(root_obj_id)
            }
        }
