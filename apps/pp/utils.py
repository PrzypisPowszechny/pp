from rest_framework import serializers


def data_wrapped(serializer):
    if isinstance(serializer, serializers.BaseSerializer):
        serializer_class = serializer.__class__
    else:
        # Initialize if class was passed instead of instance
        serializer_class = serializer
        serializer = serializer_class()
    return type('%sData' % serializer_class.__name__, (serializers.Serializer,), {'data': serializer})


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
