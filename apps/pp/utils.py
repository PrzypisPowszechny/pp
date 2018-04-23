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


def get_jsonapimeta(obj, attr=None):
    model = obj
    if isinstance(obj, models.Model):
        if attr not in (None, 'pk', 'id'):
            model = obj._meta.get_field(attr).related_model
    elif isinstance(obj, models.QuerySet):
        model = obj.model
    return model.JSONAPIMeta


def get_resource_name(obj, attr=None, jsonapimeta=None):
    meta = jsonapimeta or get_jsonapimeta(obj, attr)
    name = getattr(meta, 'resource_name', None)
    if name is not None:
        return name
    get_names = getattr(meta, 'get_resource_names', None)
    if get_names is not None:
        return get_names(obj.__dict__ if obj else {})
    raise ValueError('obj need to have either resource_name or get_resource_names defined')


def set_relationship(root_data, root_obj, obj, attr=None, jsonapimeta=None):
    resource = get_resource_name(obj, attr, jsonapimeta)
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
            'links': root_obj.id
        }


def set_relationship_many(root_data, obj, attr, override_val=None):
    resource = get_resource_name(obj, attr)
    objs = override_val if override_val is not None else getattr(obj, attr)
    if isinstance(objs, models.Manager):
        objs = objs.all()
    data_list = []
    for obj in objs:
        data_list.append({
            'type': resource, 'id': obj.id
        })
    root_data.setdefault('relationships', {})[resource] = {
        'data': data_list,
        'links': obj.id
    }


def get_resource_self_link(obj):
    return reverse(obj.JSONAPIMeta.resource_link_url_name,
                   kwargs={obj.JSONAPIMeta.resource_link_url_kwarg: obj.pk})


def set_self_link(root_data, obj):
    root_data.setdefault('links', {})['self'] = get_resource_self_link(obj)
