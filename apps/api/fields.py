"""

An intro to REST framework serializers' serialization & deserialization flow that will help to play with defining
new fields.

class ChildSerializer(serializers.Serializer):
    my_char_field = serializers.CharField()

class ParentSerializer(serializers.Serializer):
    my_child_serializer = ChildSerializer()


Deserializing flow:

serializer = ParentSerializer(data={...})
serializer.is_valid()
---> ParentSerializer.IS_VALID()

    ParentSerializer.run_validation(data=self.data)
    ---> ParentSerializer.RUN_VALIDATION(data)

        is_empty, data = ParentSerializer.validate_empty_values(data)
        ---> ParentSerializer.VALIDATE_EMPTY_VALUES(data)

            if data in (empty, None): return True, self.get_default()
            else: return False, data
        if not is_empty: ParentSerializer.to_internal_value(data)
        ---> ParentSerializer.TO_INTERNAL_VALUE(data)

            value = ChildSerializer.get_value(dictionary=data)
            ---> ChildSerializer.GET_VALUE(dictionary)
            
                return dictionary[self.field_name]
            value = ChildSerializer.run_validation(data=value)
            ---> ChildSerializer.RUN_VALIDATION(data)

                data = ChildSerializer.validate_empty_values(data)
                ---> ChildSerializer.VALIDATE_EMPTY_VALUES(data)

                    if data in (empty, None): return True, self.get_default()
                    else: return False, data
                if not is_empty: ChildSerializer.to_internal_value(data)
                ---> ChildSerializer.TO_INTERNAL_VALUE(data)

                    value = Field.get_value(dictionary=data)
                    ---> Field.GET_VALUE(dictionary)
            
                        return dictionary[self.field_name]
                    value = Field.run_validation(data=value)
                    ---> Field.RUN_VALIDATION(data)

                        if data in (empty, None) return self.get_default()
                        ---> Field.VALIDATE_EMPTY_VALUES(data)

                            if data in (empty, None): return True, self.get_default()
                            else: return False, data
                        if not is_empty: Field.to_internal_value(data)
                        ---> Field.TO_INTERNAL_VALUE(data)

                            return data

Serializing flow:

response_data = serializer(instance=MyModel).data
---> @property ParentSerializer.DATA()

    ParentSerializer.to_representation(instance)
    ---> ParentSerializer.TO_REPRESENTATION(instance)

        attribute = ChildSerializer.get_attribute(instance)
        ---> ChildSerializer.GET_ATTRIBUTE(instance)

            return instance.get(self.field_name) or getattr(instance, self.field_name) or self.get_default()
        if attribute is not None: ChildSerializer.to_representation(instance=attribute)
        ---> ChildSerializer.TO_REPRESENTATION(instance)

            attribute = Field.get_attribute(instance)
            ---> Field.GET_ATTRIBUTE(instance)

                return instance.get(self.field_name) or getattr(instance, self.field_name) or self.get_default()
            if attribute is not None: Field.to_representation(value=attribute)
            ---> Field.TO_REPRESENTATION(value)

                return value
"""
import json

import copy
import inflection
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, fields

from apps.annotation.utils import standardize_url


class IDField(serializers.IntegerField):
    """
    Field for strings containing valid integers and for pure None
    """

    def to_internal_value(self, data):
        if data is None:
            return None
        return super().to_internal_value(data)

    def to_representation(self, value):
        value = getattr(value, 'id', None) or value
        if value is None:
            return None
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
        if value is None:
            return None
        return {
            'type': self.type_subfield.to_representation(None),
            'id': self.id_subfield.to_representation(value)
        }


def custom_none():
    """
    In short: universal constant designed to mark the value as custom none which doesn't simply mean whole output of
              field is None, but that the field want to handle it and produce output using to_representation

    It does not change reference even if called (as class-based const does).

    We assume such scenario:

        class MySerializer(serializers.Serializer):
            my_field = serializers.CharField(default=...)

        response_data = MySerializer(instance=...).data


    Thorough comparison of values of default argument:

        `not in (empty, None)` –  default is supplied, it will be passed to `to_representation` where the field
                   will transform internal value to representation.
        `empty` –  argument `default` was ignored and is undefined. If value for serialization isn't supplied
                   error will be raised during serialization.
        `None`  –  default is supplied but is interpreted by serializer that the value for the field is not required
                   (no exception). Output will be set just to None without passing it to `to_representation`
                   where field transforms internal values to representation.


    so here comes custom_none:

        `custom_none` – default is supplied and is not equal to None, so the field is not omitted by the serializer
                        and field itself can decide what is it's "none output` by implementing in `to_representation`
                        following flow: `if value is custom_none`

    """
    return custom_none


class Default:
    def __init__(self, run):
        self.serializer = None
        self.run = run

    def __call__(self):
        self.run(self)

    def set_context(self, serializer):
        self.serializer = serializer


class RelationField(serializers.Field):
    child = fields._UnvalidatedField()
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

    def validate_empty_values(self, data):
        """
        If during validation field defaulted to `custom_none`, mark it as non empty value, so that it will processed
        further to to_internal_value.
        """
        is_empty_value, data = super().validate_empty_values(data)
        return is_empty_value and data != custom_none, data

    def get_attribute(self, instance):
        """
        This fields has representation for `None` as well, so set temporary `custom_none` that will be treated as `None`
        and properly handled by to_representation.
        """
        attribute = super().get_attribute(instance)
        return self.to_custom_none(attribute)

    def to_internal_value(self, data):
        if data is custom_none:
            return self.child.run_validation(self.from_custom_none(data))
        if not isinstance(data, dict):
            self.fail('not_a_dict', input_type=type(data).__name__)
        if 'data' not in data:
            self.fail('data_missing')
        return self.child.run_validation(data['data'])

    def to_representation(self, instance):
        instance = self.from_custom_none(instance)

        root_obj_id = getattr(self.context['root_resource_obj'], 'id', None) or self.context.get('root_resource_obj')
        assert isinstance(root_obj_id, (str, int)), "{cls} requires root_resource_obj (id or obj with id attr) to be " \
                                                    "supplied in context' ".format(cls=self.__class__.__name__)

        data_value = self.child.to_representation(instance)

        return {
            'data': data_value,
            'links': {
                'related': self.link_child.to_representation(root_obj_id)
            }
        }

    def to_custom_none(self, value):
        return custom_none if value is None else value

    def from_custom_none(self, value):
        if value is custom_none:
            return [] if self.many else None
        return value
