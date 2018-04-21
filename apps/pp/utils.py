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


def get_resource_name(model, attr=None):
    if attr not in (None, 'pk', 'id'):
        model = model._meta.get_field(attr).related_model
    return model.JSONAPIMeta.resource_name

def set_relationship(root_data, obj, attr):
    resource = get_resource_name(obj, attr)
    val = getattr(obj, attr)
    if val is None:
        data = None
    else:
        data = {
            'type': resource, 'id': val
        }
    root_data.setdefault('relationships', {})[resource[:-1]] = {'data': data}


def get_resource_self_link(obj):
    return reverse(obj.JSONAPIMeta.resource_link_url_name,
                   kwargs={obj.JSONAPIMeta.resource_link_url_kwarg: obj.pk})


def set_self_link(root_data, obj):
    root_data.setdefault('links', {})['self'] = get_resource_self_link(obj)
