import inflection
from django.test import TestCase
from parameterized import parameterized
from rest_framework import serializers

from apps.annotation import serializers2
from apps.annotation.serializers2 import ConstField
from mock import patch, MagicMock


class SerializersTest(TestCase):
    fake_url_name = 'fake_url_name'
    fake_url = 'fake://fake.fake/fake/'
    fake_resource_name = 'fake_resources'
    fake_root_id = '123'
    fake_related_id = '987'

    def get_serializer_class(self, **kwargs):
        class Relations(serializers.Serializer):
            my_relation = serializers2.RelationField(
                related_link_url_name=self.fake_url_name,
                child=serializers2.ResourceField(resource_name=self.fake_resource_name),
                **kwargs
            )
        return Relations

    # @parameterized.expand([(x,y])
    def test_single_relation_serializer(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.serializers2.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': self.fake_related_id},
                context={
                    'request': mock_request,
                    'root_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': {
                        'type': inflection.camelize(self.fake_resource_name, uppercase_first_letter=False),
                        'id': self.fake_related_id
                    },
                    'links': {
                        'related': self.fake_url
                    }
                }
            })

    def test_relation_serializer__single__none(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.serializers2.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': None},
                context={
                    'request': mock_request,
                    'root_obj': self.fake_root_id
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

    def test_relation_serializer__single__none_2(self):
        serializer_class = self.get_serializer_class()
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.serializers2.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={},
                context={
                    'request': mock_request,
                    'root_obj': self.fake_root_id
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
        serializer_class = self.get_serializer_class(many=True)
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.serializers2.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': []},
                context={
                    'request': mock_request,
                    'root_obj': self.fake_root_id
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

    def test_relation_serializer__many__empty_list(self):
        serializer_class = self.get_serializer_class(many=True)
        mock_request = MagicMock(build_absolute_uri=lambda val: val)

        with patch('apps.annotation.serializers2.reverse', return_value=self.fake_url):
            serializer = serializer_class(
                instance={'my_relation': [self.fake_related_id]},
                context={
                    'request': mock_request,
                    'root_obj': self.fake_root_id
                }
            )
            self.assertDictEqual(serializer.data, {
                'my_relation': {
                    'data': [{
                            'type': inflection.camelize(self.fake_resource_name, uppercase_first_letter=False),
                            'id': self.fake_related_id
                    }],
                    'links': {
                        'related': self.fake_url
                    }
                }
            })
