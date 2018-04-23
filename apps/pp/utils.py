import collections

from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import serializers


def data_wrapped(wrapped_serializer, *args, **kwargs):
    if isinstance(wrapped_serializer, serializers.BaseSerializer):
        wrapped_serializer_class = wrapped_serializer.__class__
    else:
        # Initialize if class was passed instead of instance
        wrapped_serializer_class = wrapped_serializer
        wrapped_serializer = wrapped_serializer_class()
    wrapper_field_class = type('%sData' % wrapped_serializer_class.__name__,
                               (serializers.Serializer,),
                               {'data': wrapped_serializer})
    return wrapper_field_class(*args, **kwargs)


def get_relationship_id(root_serializer, name):
    path = ['relationships', name, 'data', 'id']
    val = root_serializer.validated_data
    while path and val:
        key = path.pop(0)
        val = val.get(key)
    return val


def get_jsonapimeta(obj, related_field=None):
    model = obj
    if isinstance(obj, models.Model):
        if related_field and related_field not in ('pk', 'id'):
            model = obj._meta.get_field(related_field).related_model
    elif isinstance(obj, models.QuerySet):
        model = obj.model
    return model.JSONAPIMeta


def get_resource_name(obj, related_field=None, model=None):
    meta = get_jsonapimeta(model if model else obj, related_field)
    name = getattr(meta, 'resource_name', None)
    if name is not None:
        return name
    get_names = getattr(meta, 'get_resource_names', None)
    if get_names is not None:
        return get_names(obj)
    raise ValueError('obj need to have either resource_name or get_resource_names defined')


class DataPreSetter(object):
    def __init__(self, root_obj, root_data=None):
        self.root_data = root_data if root_data is not None else {}
        self.root_obj = root_obj

        self.root_data.setdefault('id', self.root_obj.id)
        self.root_data.setdefault('type', get_resource_name(self.root_obj))
        self.root_data.setdefault('links', {}).setdefault('self', get_resource_self_link(self.root_obj))

    @property
    def data(self):
        return self.root_data

    def set_relation(self, resource_name, resource_id):
        # resource_names_map is dict of resource_names with falses and only one true
        # for the only one relation we want to use resource_id with.
        resource_names_map = {resource_name: True} if not isinstance(resource_name, collections.Mapping) \
            else resource_name
        is_single_relation = not isinstance(resource_id, collections.Iterable)
        if is_single_relation:
            resource_id = [resource_id] if resource_id is not None else []

        for res_name, use_res_id in resource_names_map.items():
            res_key_name = res_name[:-1] if is_single_relation else res_name
            if not use_res_id or not resource_id:
                data = None if is_single_relation else []
            else:
                data = []
                for res_id in resource_id:
                    data.append({
                        'type': res_name, 'id': getattr(res_id, 'id', None) or res_id,
                    })
                if is_single_relation:
                    data = data[0]
            self.root_data.setdefault('relationships', {})[res_key_name] = {
                'data': data,
                'links': self.root_obj.id
            }


def set_simple_relationship(root_data, root_obj, resource_name, resource_id):
    # resource_names_map is dict of resource_names with falses and only one true
    # for the only one relation we want to use resource_id with.
    resource_names_map = {resource_name: True} if not isinstance(resource_name, collections.Mapping) else resource_name
    is_single_relation = not isinstance(resource_id, collections.Iterable)
    if is_single_relation:
        resource_id = [resource_id] if resource_id is not None else []

    for res_name, use_res_id in resource_names_map.items():
        res_key_name = res_name[:-1] if is_single_relation else res_name
        if not use_res_id or not resource_id:
            data = None if is_single_relation else []
        else:
            data = []
            for res_id in resource_id:
                data.append({
                    'type': res_name, 'id': getattr(res_id, 'id', None) or res_id,
                })
            if is_single_relation:
                data = data[0]
        root_data.setdefault('relationships', {})[res_key_name] = {
            'data': data,
            'links': root_obj.id
        }


def set_relationship(root_data, obj, attr=None, root_obj=None):
    resource = get_resource_name(obj, attr)
    if not isinstance(resource, dict):
        resources = {resource: True}
    else:
        resources = resource
    val = getattr(obj, attr) if obj and attr else None
    for resource, resource_is_not_none in resources.items():
        if val is None or not resource_is_not_none:
            data = None
        else:
            data = {
                'type': resource, 'id': val,
            }
        root_data.setdefault('relationships', {})[resource[:-1]] = {
            'data': data,
            'links': root_obj.id if root_obj else None
        }


def get_resource_self_link(obj):
    return reverse(obj.JSONAPIMeta.resource_link_url_name,
                   kwargs={obj.JSONAPIMeta.resource_link_url_kwarg: obj.pk})


def set_self_link(root_data, obj):
    root_data.setdefault('links', {})['self'] = get_resource_self_link(obj)
