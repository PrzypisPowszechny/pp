from collections import namedtuple
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from mock import patch
from model_mommy import mommy
from parameterized import parameterized

from apps.annotation.models import Annotation, AnnotationRequest
from apps.annotation.utils import standardize_url, standardize_url_id

JSONAPIMeta = namedtuple('JSONAPIMeta', ('resource_name',))


class StandardizeURLTest(SimpleTestCase):

    @parameterized.expand([
        # Accepts empty, returns empty
        ("",
         ""),
        # No change
        ("https://docs.python.org/",
         "https://docs.python.org/"),
        # No change
        ("http://docs.python.org/",
         "http://docs.python.org/"),
        # Add slash
        ("https://docs.python.org",
         "https://docs.python.org/"),
        # Strip fragment (anchor)
        ("https://docs.python.org/2/library/urlparse.html?a=1&b=2#urlparse-result-object",
         "https://docs.python.org/2/library/urlparse.html?a=1&b=2"),
        # Strip question mark
        ("https://docs.python.org/2/library/urlparse.html?",
         "https://docs.python.org/2/library/urlparse.html"),
        # Strip irrelevant querystring
        ("https://docs.python.org/2/library/urlparse.html?utm_campaign=buy-it&a=1",
         "https://docs.python.org/2/library/urlparse.html?a=1"),
    ])
    def test_standardize_url(self, input_url, expected_url):
        self.assertEqual(standardize_url(input_url), expected_url)


    @parameterized.expand([
        # Accepts empty, returns empty
        ("",
         ""),
        # No change
        ("docs.python.org/",
         "docs.python.org/"),
        # Remove protocol
        ("http://docs.python.org/",
         "docs.python.org/"),
        # Add slash
        ("https://docs.python.org",
         "docs.python.org/"),
        # Strip fragment (anchor)
        ("https://docs.python.org/2/library/urlparse.html?a=1&b=2#urlparse-result-object",
         "docs.python.org/2/library/urlparse.html?a=1&b=2"),
        # Strip question mark
        ("https://docs.python.org/2/library/urlparse.html?",
         "docs.python.org/2/library/urlparse.html"),
        # Strip irrelevant querystring
        ("https://docs.python.org/2/library/urlparse.html?utm_campaign=buy-it&a=1",
         "docs.python.org/2/library/urlparse.html?a=1"),
    ])
    def test_standardize_url_id(self, input_url, expected_url):
        self.assertEqual(standardize_url_id(input_url), expected_url)



# TODO: update this test to test DataPreSetter.set_relation as it is important util
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
            pass
            # This is just template of test to be used in the future
