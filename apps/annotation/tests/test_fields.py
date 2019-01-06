import inflection
from django.test import TestCase
from rest_framework import serializers

from apps.annotation import fields
from mock import patch, MagicMock


class RelationSerializerTest(TestCase):
    fake_root_id = 123
    fake_url_name = 'fake_url_name'
    fake_url = 'fake://fake.fake/fake-root-resource/{root_id}/fake-related-resource'.format(root_id=fake_root_id)
    fake_resource_name = 'fake_resources'
    any_char = 'any-fake-char'

    def get_serializer_class(self, kwargs=None, kwargs_child=None):
        class Relations(serializers.Serializer):
            my_relation = fields.RelationField(
                related_link_url_name=self.fake_url_name,
                child=serializers.CharField(**(kwargs_child if kwargs_child is not None else {})),
                **(kwargs if kwargs is not None else {})
            )
        return Relations

    def test_relation_serializer(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url) as reverse_mock:
            serializer = serializer_class(
                instance={'my_relation': self.any_char},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': self.any_char,
                    'links': {
                        'related': self.fake_url
                    }
                }
            })
            reverse_mock.assert_called_once_with(self.fake_url_name, args=[self.fake_root_id])

    def test_relation_serializer__single__none(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': None},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': None,
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_serializer__single__key_missing(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            with self.assertRaises(KeyError):
                data = serializer.data

    def test_relation_serializer__single__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'default': fields.custom_none})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': None,
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_serializer__many(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': [self.any_char]},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [self.any_char],
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_serializer__many__empty_list(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': []},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [],
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_serializer__many__key_missing(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            with self.assertRaises(KeyError):
                data = serializer.data

    def test_relation_serializer__many__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True, 'default': fields.custom_none})
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [],
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    # Deserializer

    def test_relation_deserializer__single(self):
        serializer_class = self.get_serializer_class()

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': self.any_char,
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': self.any_char})

    def test_relation_deserializer__single__none(self):
        serializer_class = self.get_serializer_class(kwargs_child={'allow_null': True})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': None,
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': None})

    def test_relation_deserializer__single__key_missing(self):
        serializer_class = self.get_serializer_class()

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={})
            self.assertFalse(serializer.is_valid())
            self.assertTrue('my_relation' in serializer.errors, msg=serializer.errors)

    def test_relation_deserializer__single__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'default': fields.custom_none})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={})
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {
                'my_relation': None
            })

    def test_relation_deserializer__many(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': [],
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': []})

    def test_relation_deserializer__many__empty_list(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': [self.any_char],
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': [self.any_char]})

    def test_relation_deserializer__many__key_missing(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={})
            self.assertFalse(serializer.is_valid())
            self.assertTrue('my_relation' in serializer.errors, msg=serializer.errors)

    def test_relation_deserializer__many__key_missing__default(self):
        serializer_class = self.get_serializer_class(kwargs={'many': True, 'default': fields.custom_none})

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={})
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {
                'my_relation': []
            })


class ResourceRelationTest(TestCase):
    fake_url_name = 'fake_url_name'
    fake_url = 'fake://fake.fake/fake/'
    fake_resource_name = 'fake_resources'
    fake_root_id = 123
    fake_related_id = 987

    def get_serializer_class(self, **kwargs):
        class Relations(serializers.Serializer):
            my_relation = fields.RelationField(
                related_link_url_name=self.fake_url_name,
                child=fields.ResourceField(resource_name=self.fake_resource_name),
                **kwargs
            )
        return Relations

    # @parameterized.expand([(x,y])
    def test_relation_serializer(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': self.fake_related_id},
                context={
                    'request': mock_request,
                    'root_resource_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': {
                        'type': inflection.camelize(self.fake_resource_name, uppercase_first_letter=False),
                        'id': str(self.fake_related_id)
                    },
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_deserializer(self):
        serializer_class = self.get_serializer_class()

        with patch('apps.annotation.fields.reverse', return_value=self.fake_url):
            serializer = serializer_class(data={
                'my_relation': {
                    'data': {
                        'type': inflection.camelize(self.fake_resource_name, uppercase_first_letter=False),
                        'id': self.fake_related_id
                    },
                },
            })
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            self.assertDictEqual(serializer.validated_data, {'my_relation': self.fake_related_id})
