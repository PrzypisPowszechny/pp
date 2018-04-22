from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from mock import patch
from model_mommy import mommy
from parameterized import parameterized

from apps.pp.models import Reference, ReferenceRequest
from apps.pp.utils import set_relationship

JSONAPIMeta = namedtuple('JSONAPIMeta', ('resource_name',))


class SetRelationshipTest(SimpleTestCase):
    @parameterized.expand([
        # User, overwrite resource name, with id
        (mommy.prepare(
            Reference,
            user=mommy.prepare(
                get_user_model(),
                id=123
            )
         ).user,
         'non_standard_users',
         {
            'relationships': {
                'non_standard_user': {
                    'data': {
                        'type': 'non_standard_users',
                        'id': 123
                    }
                }
            }
         }),
        # ReferenceRequest, default resource name, with id
        (mommy.prepare(
            Reference,
            reference_request=mommy.prepare(
                ReferenceRequest,
                id=123
            )
         ).reference_request,
         None,
         {
            'relationships': {
                'reference_request': {
                    'data': {
                        'type': 'reference_requests',
                        'id': 123
                    }
                }
            }
         }),
        # User, overwrite resource name, no id
        (mommy.prepare(
            Reference,
            user=mommy.prepare(
                get_user_model(),
                id=None
            )
         ).user,
         'non_standard_users',
         {
            'relationships': {
                'non_standard_user': {
                    'data': None
                }
            }
         }),
        # ReferenceRequest, default resource name, no id
        (mommy.prepare(
            Reference,
            reference_request=mommy.prepare(
                ReferenceRequest,
                id=None
            )
         ).reference_request,
         None,
         {
            'relationships': {
                'reference_request': {
                    'data': None
                }
            }
         }),

    ])
    def test_set_relationship_pk_attr(self, obj, resource_name, expected_data):
        meta = obj.JSONAPIMeta
        with patch.object(meta, 'resource_name', resource_name or meta.resource_name):
            data = {}
            set_relationship(data, obj, attr='pk')
            self.assertDictEqual(data, expected_data)

    @parameterized.expand([
        # User, overwrite resource name, with id
        (mommy.prepare(
            Reference,
            user=mommy.prepare(
                get_user_model(),
                id=123
            )
         ),
         'user_id',
         'non_standard_users',
         {
            'relationships': {
                'non_standard_user': {
                    'data': {
                        'type': 'non_standard_users',
                        'id': 123
                    }
                }
            }
         }),
        # ReferenceRequest, default resource name, with id
        (mommy.prepare(
            Reference,
            reference_request=mommy.prepare(
                ReferenceRequest,
                id=123
            )
         ),
         'reference_request_id',
         None,
         {
            'relationships': {
                'reference_request': {
                    'data': {
                        'type': 'reference_requests',
                        'id': 123
                    }
                }
            }
         }),
        # User, overwrite resource name, no id
        (mommy.prepare(
            Reference,
            user=mommy.prepare(
                get_user_model(),
                id=None
            )
         ),
         'user_id',
         'non_standard_users',
         {
            'relationships': {
                'non_standard_user': {
                    'data': None
                }
            }
         }),
        # ReferenceRequest, default resource name, no id
        (mommy.prepare(
            Reference,
            reference_request=mommy.prepare(
                ReferenceRequest,
                id=None
            )
         ),
         'reference_request_id',
         None,
         {
            'relationships': {
                'reference_request': {
                    'data': None
                }
            }
         }),

    ])
    def test_set_relationship_fk_attr(self, obj, attr, resource_name, expected_data):
        meta = obj._meta.get_field(attr).related_model.JSONAPIMeta
        with patch.object(meta, 'resource_name', resource_name or meta.resource_name):
            data = {}
            set_relationship(data, obj, attr=attr)
            self.assertDictEqual(data, expected_data)
