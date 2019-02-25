import inflection
from django.test import TestCase
from mock import patch, MagicMock
from rest_framework import serializers

from apps.api import fields


class RelationSerializerTest(TestCase):
    my_root_id = 123
    my_url_name = 'an_url_name'
    my_url = 'http://example.com/root_resources/{root_id}/related_resource'.format(root_id=my_root_id)
    my_resource_name = 'my_resources'
    my_string = 'unique-char-data'

    def get_serializer_class(self, kwargs=None, kwargs_child=None):
        class Relations(serializers.Serializer):
            my_relation = fields.RelationField(
                related_link_url_name=self.my_url_name,
                child=serializers.CharField(**(kwargs_child if kwargs_child is not None else {})),
                **(kwargs if kwargs is not None else {})
            )

        return Relations

    # Serializer Single

    def test_single(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url) as reverse_mock:
            serializer = serializer_class(
                instance={'my_relation': self.my_string},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': self.my_string,
                    'links': {
                        'related': self.my_url
                    }
                }
            })
            reverse_mock.assert_called_once_with(self.my_url_name, args=[self.my_root_id])

    def test_single__none(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={'my_relation': None},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    # This field type is char, so None is converted to char as well
                    'data': 'None',
                    'links': {
                        'related': self.my_url
                    }
                }
            })

    def test_single__key_missing(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            with self.assertRaises(KeyError):
                data = serializer.data

    def test_single__key_missing__not_required(self):
        serializer_class = self.get_serializer_class(kwargs={'required': False})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {})

    def test_single__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'default': fields.custom_none})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    # This field type is char, so None is converted to char as well
                    'data': 'None',
                    'links': {
                        'related': self.my_url
                    }
                }
            })

    # Serializer Many

    def test_many(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={'my_relation': [self.my_string]},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [self.my_string],
                    'links': {
                        'related': self.my_url
                    }
                }
            })

    def test_many__empty_list(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={'my_relation': []},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [],
                    'links': {
                        'related': self.my_url
                    }
                }
            })

    def test_many__key_missing(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            with self.assertRaises(KeyError):
                data = serializer.data

    def test_many__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True, 'default': fields.custom_none})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.my_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [],
                    'links': {
                        'related': self.my_url
                    }
                }
            })

    # Deserializer Single

    def test_deserializer_single(self):
        serializer_class = self.get_serializer_class()

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': self.my_string,
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': self.my_string})

    def test_deserializer_single__none(self):
        serializer_class = self.get_serializer_class(kwargs_child={'allow_null': True})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': None,
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': None})

    def test_deserializer_single__key_missing(self):
        serializer_class = self.get_serializer_class()

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={})
            self.assertFalse(serializer.is_valid())
            self.assertTrue('my_relation' in serializer.errors, msg=serializer.errors)

    def test_deserializer_single__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'default': fields.custom_none},
                                                     kwargs_child={'allow_null': True})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={})
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {
                'my_relation': None
            })

    # Deserializer Many

    def test_deserializer_many(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': [],
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': []})

    def test_deserializer_many__empty_list(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': [self.my_string],
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': [self.my_string]})

    def test_deserializer_many__key_missing(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={})
            self.assertFalse(serializer.is_valid())
            self.assertTrue('my_relation' in serializer.errors, msg=serializer.errors)

    def test_deserializer_many__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True, 'default': fields.custom_none})

        with patch('apps.api.fields.reverse', return_value=self.my_url):
            serializer = serializer_class(data={})
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {
                'my_relation': []
            })


class ResourceTest(TestCase):
    my_resource_name = 'my_resources'
    my_related_id = 987

    def get_serializer_class(self, **kwargs):
        class Resources(serializers.Serializer):
            my_resource_data = fields.ResourceField(resource_name=self.my_resource_name)

        return Resources

    def test_serializer(self):
        serializer_class = self.get_serializer_class()

        serializer = serializer_class(
            instance={'my_resource_data': self.my_related_id}
        )
        self.assertDictEqual(serializer.data, {
            'my_resource_data': {
                'type': inflection.camelize(self.my_resource_name, uppercase_first_letter=False),
                'id': str(self.my_related_id)
            },
        })

    def test_deserializer(self):
        serializer_class = self.get_serializer_class()

        serializer = serializer_class(data={
            'my_resource_data': {
                'type': inflection.camelize(self.my_resource_name, uppercase_first_letter=False),
                'id': str(self.my_related_id)
            },
        })
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertDictEqual(serializer.validated_data, {'my_resource_data': self.my_related_id})
