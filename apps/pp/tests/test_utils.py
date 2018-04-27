from collections import namedtuple
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from mock import patch
from model_mommy import mommy
from parameterized import parameterized

from apps.pp.models import Annotation, AnnotationRequest
from apps.pp.utils import set_relationship

JSONAPIMeta = namedtuple('JSONAPIMeta', ('resource_name',))


@skip
class SetRelationshipTest(SimpleTestCase):

    @parameterized.expand([
        # User, overwrite resource name, with id
        (mommy.prepare(
            Annotation,
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
        # AnnotationRequest, default resource name, with id
        (mommy.prepare(
            Annotation,
            annotation_request=mommy.prepare(
                AnnotationRequest,
                id=123
            )
        ).annotation_request,
         None,
         {
             'relationships': {
                 'annotation_request': {
                     'data': {
                         'type': 'annotation_requests',
                         'id': 123
                     }
                 }
             }
         }),
        # User, overwrite resource name, no id
        (mommy.prepare(
            Annotation,
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
        # AnnotationRequest, default resource name, no id
        (mommy.prepare(
            Annotation,
            annotation_request=mommy.prepare(
                AnnotationRequest,
                id=None
            )
        ).annotation_request,
         None,
         {
             'relationships': {
                 'annotation_request': {
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
            Annotation,
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
        # AnnotationRequest, default resource name, with id
        (mommy.prepare(
            Annotation,
            annotation_request=mommy.prepare(
                AnnotationRequest,
                id=123
            )
        ),
         'annotation_request_id',
         None,
         {
             'relationships': {
                 'annotation_request': {
                     'data': {
                         'type': 'annotation_requests',
                         'id': 123
                     }
                 }
             }
         }),
        # User, overwrite resource name, no id
        (mommy.prepare(
            Annotation,
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
        # AnnotationRequest, default resource name, no id
        (mommy.prepare(
            Annotation,
            annotation_request=mommy.prepare(
                AnnotationRequest,
                id=None
            )
        ),
         'annotation_request_id',
         None,
         {
             'relationships': {
                 'annotation_request': {
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
