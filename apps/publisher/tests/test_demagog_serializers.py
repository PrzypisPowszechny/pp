from django.test import TestCase
from django.utils import timezone
from parameterized import parameterized

from apps.publisher.serializers import StatementDeserializer, SourcesDeserializer

SOURCE_URL = 'http://i-am-article-you-check.org'
FACT_URL = 'http://i-check-you-all.org'


class SerializersTest(TestCase):
    maxDiff = None

    def setUp(self):
        pass

    def get_statement_valid_attrs(self):
        return {
            'source': SOURCE_URL,
            'text': "it's an interesting article",
            'date':  timezone.now(),
            'rating': 'true',
            'rating_text':'true statement',
            'factchecker_uri': FACT_URL
        }

    def get_statement_valid_data(self):
        return {
            'id': 1,
            'attributes': self.get_statement_valid_attrs()
        }

    def test_statement_deserializer__accept_valid(self):
        deserializer = StatementDeserializer(data=self.get_statement_valid_data())
        self.assertTrue(deserializer.is_valid())

    @parameterized.expand([
        [{'id': None}, {}],
        [{'id': 'string-id'}, {}],
        [{}, {'source': ''}],
        [{}, {'source': 'not-valid-url'}],
        [{}, {'text': ''}],
        [{}, {'rating': ''}],
        [{}, {'rating': 'not-in-choices'}],
        [{}, {'rating_text': ''}],
        [{}, {'factchecker_uri': ''}],
        [{}, {'factchecker_uri': 'not-valid-url'}],
        [{}, {'date': ''}],
        [{}, {'date': 'not-valid-date'}],
    ])
    def test_statement_deserializer__invalid_field_value(self, override_data, override_attributes):
        data = self.get_statement_valid_data()
        data.update(override_data)
        data['attributes'].update(override_attributes)

        deserializer = StatementDeserializer(data=data)
        self.assertFalse(deserializer.is_valid())

    @parameterized.expand([
        [True, {'attributes': {'sources': []}}],
        [True, {'attributes': {'sources': [FACT_URL, SOURCE_URL]}}],
        [False, {'attributes': {'sources': ['not-an-url']}}],
        [False, {'attributes': {'sources': None}}],
        [False, {'attributes': None}],
        [False, None],
    ])
    def test_sources_deserializer(self, is_valid, data):
        deserializer = SourcesDeserializer(data=data)
        self.assertEqual(deserializer.is_valid(), is_valid)
