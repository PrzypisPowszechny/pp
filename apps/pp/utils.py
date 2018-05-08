import collections
from urllib.parse import urlencode, parse_qsl, urlsplit

from django.db import models


def get_relationship_id(root_serializer, name):
    """
    Use only when passing relation with url parameter does not do the job.
    """
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


def get_resource_name(obj, related_field=None, model=None, always_single=False):
    meta = get_jsonapimeta(model if model else obj, related_field)
    return getattr(meta, 'resource_name', None)


class DataPreSerializer(object):
    def __init__(self, root_obj, root_data=None):
        self.root_data = root_data if root_data is not None else {}
        self.root_obj = root_obj

        self._root_resource_name = get_resource_name(self.root_obj, always_single=True)
        self.root_data.setdefault('id', self.root_obj.id)
        self.root_data.setdefault('type', self._root_resource_name)
        self.root_data.setdefault('links', self.root_obj)

    @property
    def data(self):
        return self.root_data

    def get_relation_name(self, resource_name, is_single_relation):
        """
        If resource name of the main object is prefix of resource name of relation then
        remove that prefix to make relation name shorter"
        For example:
         - main resource "annotation", related resource "annotation_reports" -> relation name "reports"
         - main resource "annotation_x", related resource "annotation_y" -> relation name "y"

        """
        rrn, rn = self._root_resource_name, resource_name
        prefix = rrn[:rrn.find('_')] if rrn.find('_') > 0 else rrn[:-1]
        if rn.find('_') > 0 and rn.startswith(prefix):
            name = rn[len(prefix) + 1:]
        else:
            name = rn
        return name[:-1] if is_single_relation else name

    def set_relation(self, resource_name, resource_id, relation_name=None):
        # resource_names_map is dict of resource_names with falses and only one true
        # for the only one relation we want to use resource_id with.
        if isinstance(resource_name, collections.Mapping):
            assert relation_name is None, "relation_name param can be used when resource_name is string not mapping"
        resource_names_map = {resource_name: True} if not isinstance(resource_name, collections.Mapping) \
            else resource_name
        is_single_relation = not isinstance(resource_id, collections.Iterable)
        if is_single_relation:
            resource_id = [resource_id] if resource_id is not None else []

        for res_name, use_res_id in resource_names_map.items():
            res_key_name = relation_name or self.get_relation_name(resource_name, is_single_relation)
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


OMITTED_QUERY_VARS = (
    'utm_campaign',
    'utm_medium',
)


def standardize_url_index(data):
    """
    Format url in the way that:
      - ignores protocol
      - ignores fragment(anchor)
      - ignores some blacklisted query vars like utm etc
      - set '/' as a path if none given
      - removes '?' if no query string
    """
    url_parsed = urlsplit(data)
    query_tuples = parse_qsl(url_parsed.query)
    new_query_tuples = []
    for var_name, val in query_tuples:
        if var_name not in OMITTED_QUERY_VARS:
            new_query_tuples.append((var_name, val))
    return '{netloc}{path}{query}'.format(
        netloc=url_parsed.netloc,
        path=url_parsed.path if url_parsed.path else '/',
        query='?' + urlencode(new_query_tuples) if new_query_tuples else ''
    )


def standardize_url(data):
    """
        Format url in the way that:
          - ignores fragment(anchor)
          - ignores some blacklisted query vars like utm etc
          - set '/' as a path if none given
          - removes '?' if no query string
        """
    url_parsed = urlsplit(data)
    query_tuples = parse_qsl(url_parsed.query)
    new_query_tuples = []
    for var_name, val in query_tuples:
        if var_name not in OMITTED_QUERY_VARS:
            new_query_tuples.append((var_name, val))
    return '{scheme}://{netloc}{path}{query}'.format(
        scheme=url_parsed.scheme,
        netloc=url_parsed.netloc,
        path=url_parsed.path if url_parsed.path else '/',
        query='?' + urlencode(new_query_tuples) if new_query_tuples else ''
    )